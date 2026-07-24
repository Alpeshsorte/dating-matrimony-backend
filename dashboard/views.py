from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from chat.models import Conversation, Message
from dashboard.models import DashboardSettings
from dating.models import Match
from notifications.models import Notification
from profiles.models import Profile
from reports.models import Report
from subscriptions.models import Plan, Subscription
from django.utils import timezone


class PlanForm(ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'description', 'price', 'duration_days', 'is_active']


class DashboardSettingsForm(ModelForm):
    class Meta:
        model = DashboardSettings
        fields = ['site_name', 'support_email', 'otp_expiry_minutes', 'maintenance_mode']


class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'kind', 'title', 'body']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.filter(is_active=True).order_by('username')


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def dashboard_login(request):
    if is_staff_user(request.user):
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard:home')

        messages.error(request, 'Enter valid staff account credentials.')

    return render(request, 'dashboard/login.html')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def dashboard_home(request):
    today = timezone.localdate()
    start_date = today - timedelta(days=6)
    daily_registrations = {
        item['day']: item['count']
        for item in User.objects.filter(date_joined__date__gte=start_date)
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
    }
    chart_items = [
        {'label': (start_date + timedelta(days=index)).strftime('%d %b'), 'count': daily_registrations.get(start_date + timedelta(days=index), 0)}
        for index in range(7)
    ]
    max_registrations = max((item['count'] for item in chart_items), default=0)
    for item in chart_items:
        item['height'] = max(8, (item['count'] / max_registrations * 100)) if max_registrations else 8

    context = {
        'total_users': User.objects.count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'profile_count': Profile.objects.count(),
        'conversation_count': Conversation.objects.count(),
        'active_subscription_count': Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
        'active_subscription_revenue': Subscription.objects.filter(status=Subscription.Status.ACTIVE).aggregate(total=Sum('plan__price'))['total'] or 0,
        'chart_items': chart_items,
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'dashboard/home.html', context)


@user_passes_test(is_staff_user, login_url='dashboard:login')
def user_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    verified = request.GET.get('verified', '')
    users = User.objects.order_by('-date_joined')

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'blocked':
        users = users.filter(is_active=False)
    if verified == 'yes':
        users = users.filter(is_verified=True)
    elif verified == 'no':
        users = users.filter(is_verified=False)

    return render(request, 'dashboard/users.html', {
        'page_obj': Paginator(users, 10).get_page(request.GET.get('page')),
        'query': query, 'status': status, 'verified': verified,
    })


@user_passes_test(is_staff_user, login_url='dashboard:login')
def toggle_user_status(request, user_id):
    if request.method != 'POST':
        return redirect('dashboard:users')

    user = get_object_or_404(User, pk=user_id)
    if user == request.user or user.is_superuser:
        messages.error(request, 'This account cannot be blocked or unblocked here.')
    else:
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f'{user.username} was {"unblocked" if user.is_active else "blocked"}.')
    return redirect('dashboard:users')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def toggle_user_verification(request, user_id):
    if request.method != 'POST':
        return redirect('dashboard:users')

    user = get_object_or_404(User, pk=user_id)
    if user.is_superuser:
        messages.error(request, 'A superuser verification status cannot be changed here.')
    else:
        user.is_verified = not user.is_verified
        user.save(update_fields=['is_verified'])
        messages.success(request, f'{user.username} was {"verified" if user.is_verified else "marked unverified"}.')
    return redirect('dashboard:users')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def profile_list(request):
    status = request.GET.get('status', '')
    profiles = Profile.objects.select_related('user').order_by('-created_at')
    if status == 'pending':
        profiles = profiles.filter(is_approved=False)
    elif status == 'approved':
        profiles = profiles.filter(is_approved=True)
    elif status == 'hidden':
        profiles = profiles.filter(is_hidden=True)

    return render(request, 'dashboard/profiles.html', {
        'page_obj': Paginator(profiles, 10).get_page(request.GET.get('page')),
        'status': status,
    })


@user_passes_test(is_staff_user, login_url='dashboard:login')
def toggle_profile_approval(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, pk=profile_id)
        profile.is_approved = not profile.is_approved
        profile.save(update_fields=['is_approved', 'updated_at'])
        messages.success(request, f'{profile} was {"approved" if profile.is_approved else "moved to pending"}.')
    return redirect('dashboard:profiles')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def toggle_profile_visibility(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, pk=profile_id)
        profile.is_hidden = not profile.is_hidden
        profile.save(update_fields=['is_hidden', 'updated_at'])
        messages.success(request, f'{profile} is now {"hidden" if profile.is_hidden else "visible"}.')
    return redirect('dashboard:profiles')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def report_list(request):
    status = request.GET.get('status', '')
    reports = Report.objects.select_related('reporter', 'reported_user')
    if status in Report.Status.values:
        reports = reports.filter(status=status)

    return render(request, 'dashboard/reports.html', {
        'page_obj': Paginator(reports, 10).get_page(request.GET.get('page')),
        'status': status,
        'statuses': Report.Status.choices,
    })


@user_passes_test(is_staff_user, login_url='dashboard:login')
def update_report_status(request, report_id, status):
    if request.method == 'POST' and status in Report.Status.values:
        report = get_object_or_404(Report, pk=report_id)
        report.status = status
        report.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Report status updated.')
    return redirect('dashboard:reports')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def plan_list(request):
    plans = Plan.objects.all()
    return render(request, 'dashboard/plans.html', {
        'plans': plans,
        'active_subscription_count': Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
    })


@user_passes_test(is_staff_user, login_url='dashboard:login')
def plan_form(request, plan_id=None):
    plan = get_object_or_404(Plan, pk=plan_id) if plan_id else None
    form = PlanForm(request.POST or None, instance=plan)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Plan saved successfully.')
        return redirect('dashboard:plans')
    return render(request, 'dashboard/plan_form.html', {'form': form, 'plan': plan})


@user_passes_test(is_staff_user, login_url='dashboard:login')
def toggle_plan_status(request, plan_id):
    if request.method == 'POST':
        plan = get_object_or_404(Plan, pk=plan_id)
        plan.is_active = not plan.is_active
        plan.save(update_fields=['is_active', 'updated_at'])
        messages.success(request, f'{plan.name} was {"activated" if plan.is_active else "deactivated"}.')
    return redirect('dashboard:plans')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def chat_management(request):
    conversations = Conversation.objects.annotate(message_count=Count('messages')).prefetch_related('participants')[:20]
    reported_messages = Message.objects.filter(is_reported=True).select_related('sender', 'conversation')[:20]
    return render(request, 'dashboard/chats.html', {
        'conversation_count': Conversation.objects.count(),
        'message_count': Message.objects.count(),
        'reported_message_count': Message.objects.filter(is_reported=True).count(),
        'conversations': conversations,
        'reported_messages': reported_messages,
    })


@user_passes_test(is_staff_user, login_url='dashboard:login')
def clear_message_report(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(Message, pk=message_id)
        message.is_reported = False
        message.save(update_fields=['is_reported'])
        messages.success(request, 'Message report cleared.')
    return redirect('dashboard:chats')


@user_passes_test(is_staff_user, login_url='dashboard:login')
def dashboard_settings(request):
    settings_object, _ = DashboardSettings.objects.get_or_create(pk=1)
    form = DashboardSettingsForm(request.POST or None, instance=settings_object)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Settings saved successfully.')
        return redirect('dashboard:settings')
    return render(request, 'dashboard/settings.html', {'form': form, 'settings_object': settings_object})


@user_passes_test(is_staff_user, login_url='dashboard:login')
def notification_list(request):
    notifications = Notification.objects.select_related('recipient')
    return render(request, 'dashboard/notifications.html', {
        'page_obj': Paginator(notifications, 15).get_page(request.GET.get('page')),
    })


@user_passes_test(is_staff_user, login_url='dashboard:login')
def notification_create(request):
    form = NotificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Notification sent successfully.')
        return redirect('dashboard:notifications')
    return render(request, 'dashboard/notification_form.html', {'form': form})


@user_passes_test(is_staff_user, login_url='dashboard:login')
def match_list(request):
    status = request.GET.get('status', '')
    matches = Match.objects.select_related('requester', 'recipient')
    if status in Match.Status.values:
        matches = matches.filter(status=status)
    return render(request, 'dashboard/matches.html', {
        'page_obj': Paginator(matches, 15).get_page(request.GET.get('page')),
        'status': status,
        'statuses': Match.Status.choices,
    })


def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')
