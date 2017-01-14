from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import CategoryForm
from .models import Category


@login_required
def category_list(request):
    """
    List all categories
    """
    page = request.GET.get('page', 1)
    per_page = settings.PAGE_SIZE
    categories = request.user.categories.all()
    paginator = Paginator(categories, per_page)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        categories = paginator.page(page)
    except EmptyPage:
        page = 1
        categories = paginator.page(paginator.num_pages)

    sn = per_page * (int(page) - 1)
    context = {
        'sn': sn,
        'categories': categories
    }
    return render(request, 'categories/list.html', context)


@login_required
def category_create(request):
    """
    Create a category
    """
    form = CategoryForm(data=request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Category created.")
            return redirect("categories:create")

    context = {
        'form': form
    }
    return render(request, 'categories/create.html', context)


@login_required
def category_edit(request, pk):
    """
    Edit a category
    """
    try:
        category = request.user.categories.get(pk=pk)
    except Category.DoesNotExist:
        raise Http404()

    form = CategoryForm(instance=category, data=request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect(reverse('categories:edit', kwargs={'pk': pk}))

    context = {
        'form': form
    }
    return render(request, 'categories/edit.html', context)


@login_required
def category_delete(request, pk):
    """
    Delete a category
    """
    try:
        category = request.user.categories.get(pk=pk)
    except Category.DoesNotExist:
        raise Http404()

    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category %s deleted." % category.name)
        return redirect('categories:list')

    context = {
        'category': category
    }
    return render(request, 'categories/delete.html', context)