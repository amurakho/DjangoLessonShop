from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.views.generic.edit import FormMixin
from django.http import HttpResponse
import json

from product import models, forms


class MyFormMixin:
    form_class = None

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.queryset = self.model.objects.filter(title__contains=request.POST.get('search_field'))
        return self.get(request, *args, **kwargs)


class ProductListView(MyFormMixin, generic.ListView):
    template_name = 'product_list.html'
    model = models.Product
    context_object_name = 'products'
    form_class = forms.SearchForm

    def get(self, request, *args, **kwargs):
        print(request.session.get('viewered'))
        print(type(request.session.get('viewered')))
        return super(ProductListView, self).get(request, *args, **kwargs)


class ProductDetailView(FormMixin, generic.DetailView):
    template_name = 'product_detail.html'
    model = models.Product
    context_object_name = 'product'
    form_class = forms.CommentForm
    product_in_bucket_form = forms.ProductInBucketForm

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        context['comment_form'] = self.get_form_class()
        context['comments'] = self.get_object().comment_set.all()
        context['product_in_bucket_form'] = self.product_in_bucket_form
        return context

    def _add_product_to_viewered_container(self, container, request):
        container.append(self.object.slug)
        request.session['viewered'] = container
        return request

    def _check_not_duplicate(self, container):
        if not container:
            return True

        prev_elem = len(container) - 1
        if container[prev_elem] == self.object.slug:
            return False
        else:
            return True

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        viewered = request.session.get('viewered', [])

        if self._check_not_duplicate(viewered):
            if len(viewered) >= 5:
                viewered.pop(0)
            self._add_product_to_viewered_container(viewered, request)

        return response

    def post(self, request, *args, **kwargs):
        if request.POST.get('text'):
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            product = self.get_object()
            count = request.POST.get('count')

            product_in_bucket = models.ProductInBucket(product=product, count=count)

            bucket_id = request.session.get('bucket_id')
            if bucket_id:
                bucket = get_object_or_404(models.Bucket, id=bucket_id)
                for existed_product_in_bucket in bucket.products_in_bucket.all():
                    if existed_product_in_bucket.product == product_in_bucket.product:
                        existed_product_in_bucket.count += int(product_in_bucket.count)
                        existed_product_in_bucket.save()
                    else:
                        product_in_bucket.save()
                        bucket.products_in_bucket.add(product_in_bucket)
            else:
                bucket = models.Bucket()
                bucket.save()
                product_in_bucket.save()
                bucket.products_in_bucket.add(product_in_bucket)
                request.session['bucket_id'] = bucket.id

            bucket.update_price()
            return self.get_success_url()


    def form_valid(self, form):
        comment = models.Comment(
            text=form.cleaned_data['text'],
            rating=form.cleaned_data['rating'],
            author=self.request.user,
            product=self.get_object()
        )
        comment.save()
        return self.get_success_url()

    def get_success_url(self):
        return redirect('product_detail', slug=self.get_object().slug)