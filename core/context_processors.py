def theme_processor(request):
    if request.user.is_authenticated:
        profile = request.user.userprofile
        return {'theme': profile.theme}
    return {'theme': 'light'}