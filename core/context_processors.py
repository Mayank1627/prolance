from projects.models import Category

def global_context(request):
    """Provides platform global variables such as category lists and role flags."""
    context = {
        'site_name': 'Prolance',
        'site_tagline': 'Where Talent Meets Opportunity',
        'global_categories': Category.objects.all()[:8] if Category.objects.exists() else [],
    }
    if request.user.is_authenticated:
        context['user_is_client'] = request.user.is_client_user()
        context['user_is_freelancer'] = request.user.is_freelancer_user()
    return context

