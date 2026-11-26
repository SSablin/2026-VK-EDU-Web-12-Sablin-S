from django.contrib.auth import get_user_model
from django.core.cache import cache

from questions.models import Tag
from questions.utils import (
    BEST_MEMBERS_CACHE_KEY,
    POPULAR_TAGS_CACHE_KEY,
    calculate_best_members,
    calculate_popular_tags,
)

User = get_user_model()


def popular_tags(request):
    tag_ids = cache.get(POPULAR_TAGS_CACHE_KEY)
    if tag_ids is None:
        tags = calculate_popular_tags()
        tag_ids = [tag.id for tag in tags]
        cache.set(POPULAR_TAGS_CACHE_KEY, tag_ids, timeout=60 * 30)
    else:
        tags_by_id = {tag.id: tag for tag in Tag.objects.filter(id__in=tag_ids)}
        tags = [tags_by_id[tag_id] for tag_id in tag_ids if tag_id in tags_by_id]
    return {'popular_tags': tags}


def best_members(request):
    member_ids = cache.get(BEST_MEMBERS_CACHE_KEY)
    if member_ids is None:
        members = calculate_best_members()
        member_ids = [member.id for member in members]
        cache.set(BEST_MEMBERS_CACHE_KEY, member_ids, timeout=60 * 30)
    else:
        members_by_id = {
            member.id: member
            for member in User.objects.select_related('profile').filter(id__in=member_ids)
        }
        members = [members_by_id[member_id] for member_id in member_ids if member_id in members_by_id]
    return {"best_members": members}
