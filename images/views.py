from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action

import redis
from django.conf import settings

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        # форма отправлена
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # данные формы действительны
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # назначить текущего пользователя элементу
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'закладка изображения', new_item)
            messages.success(request, 'Изображение успешно добавлено')
            # перенаправить на подробный просмотр нового созданного элемента
            return redirect(new_item.get_absolute_url())
    else:
        # создать форму с данными, предоставленными букмарклетом через GET
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # увеличить общее количество просмотров изображений на 1
    total_views = r.incr(f'image:{image.id}:views')
    # увеличить рейтинг изображения на 1
    r.zincrby('image_ranking', 1, image.id)
    return render(request, 'images/image/detail.html', {'section': 'images',
                                                        'image': image,
                                                        'total_views': total_views})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'Нравиться':
                image.users_like.add(request.user)
                create_action(request.user, 'нравится', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 3)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом доставьте первую страницу
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # Если запрос является AJAX и страница находится вне диапазона действия
            # возвращает пустую страницу
            return HttpResponse('')
            # Если страница находится вне диапазона доставьте последнюю страницу результатов
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # получить словарь ранжирования изображений
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # получить самые просматриваемые изображения
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})
