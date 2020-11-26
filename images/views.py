from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm


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
            messages.success(request, 'Изображение успешно добавлено')
            # перенаправить на подробный просмотр нового созданного элемента
            return redirect(new_item.get_absolute_url())
    else:
        # создать форму с данными, предоставленными букмарклетом через GET
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})
