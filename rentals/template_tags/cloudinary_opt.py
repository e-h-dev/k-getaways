from django import template

register = template.Library()

@register.filter
def cloud_opt(url):
    """
    Rewrites a Cloudinary URL to include optimised transformations.
    """
    if "/upload/" not in url:
        return url  # safety fallback

    return url.replace("/upload/", "/upload/f_auto,q_auto,w_600/")
