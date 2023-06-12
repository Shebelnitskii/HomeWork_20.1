from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from .forms import ProductForm

from main.models import Product, Category, Review, Version


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"{self.object.name} {self.object.description}"
        return context


class ProductListView(generic.ListView):
    model = Product
    template_name = 'main/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        versions = Version.objects.filter(product__in=context['products'], is_current=True)
        context['versions'] = versions
        return context


class ProductCreateView(generic.CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/product_form.html'

    def get_success_url(self):
        return reverse('main:product_list')

class ProductUpdateView(generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/product_form.html'

    def get_success_url(self):
        return reverse('main:product_list')

class ProductDeleteView(generic.DeleteView):
    model = Product
    template_name = 'main/product_confirm_delete.html'

    def get_success_url(self):
        return reverse('main:product_list')

class CategoryListView(generic.ListView):
    model = Category
    template_name = 'main/category_list.html'
    context_object_name = 'object_list'
    extra_context = {'title': 'Категории'}


class ProductReviewListView(generic.ListView):
    extra_context = {'title': 'Отзывы'}
    template_name = 'main/reviews_list.html'
    context_object_name = 'reviews'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_pk = self.kwargs['pk']
        product = get_object_or_404(Product, pk=product_pk)
        context['product'] = product
        context['title'] = f"Отзыв на товар: {product.name} {product.description}"
        return context

    def get_queryset(self):
        product_pk = self.kwargs['pk']
        return Review.objects.filter(product=product_pk, is_published=True)


class ReviewCreateView(generic.CreateView):
    model = Review
    template_name = 'main/review_form.html'
    fields = ('author', 'title', 'content', 'preview')
    extra_context = {'title': 'Оставить отзыв'}

    def get_success_url(self):
        return reverse('main:product_reviews', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        initial = super().get_initial()
        initial['product'] = self.kwargs['pk']
        return initial

    def form_valid(self, form):
        form.instance.product_id = self.kwargs['pk']
        return super().form_valid(form)


class ReviewUpdateView(generic.UpdateView):
    model = Review
    template_name = 'main/review_form.html'
    fields = ('author', 'title', 'content', 'preview')
    extra_context = {'title': 'Изменить отзыв'}

    def get_success_url(self):
        return reverse('main:product_reviews', kwargs={'pk': self.object.product_id})

    def get_initial(self):
        initial = super().get_initial()
        initial['product'] = self.kwargs['pk']
        return initial

    def form_valid(self, form):
        return super().form_valid(form)


class ReviewDetailView(generic.DetailView):
    template_name = 'main/review_detail.html'
    context_object_name = 'reviews'
    name = 'review_detail.html'

    def get(self, request, *args, **kwargs):
        review = self.get_object()
        review.views_count += 1
        review.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Отзыв: {context['reviews'].author}"
        return context

    def get_queryset(self):
        review_id = self.kwargs['pk']
        return Review.objects.filter(pk=review_id)


class ReviewDeleteView(generic.DeleteView):
    model = Review
    template_name = 'main/review_confirm_delete.html'
    extra_context = {'title': 'Подтвердите удаление'}

    def get_success_url(self):
        return reverse_lazy('main:product_reviews', kwargs={'pk': self.object.product_id})
