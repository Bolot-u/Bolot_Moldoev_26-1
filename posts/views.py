from django.shortcuts import render, redirect
from posts.models import Post, Review
from posts.forms import PostCreateForm, ReviewCreateForm
from posts.constants import PAGINATION_LIMIT
from django.views.generic import ListView, CreateView, DetailView


class MainPageCBV(ListView):
    model = Post
    template_name = 'layouts/index.html'



class ProductsCBV(ListView):
    model = Post
    template_name = 'products/products.html'

    def get(self, request, **kwargs):
        posts = self.get_queryset().order_by('-created_date')
        search = request.GET.get('search')
        page = int(request.GET.get('page', 1))

        if search:
            posts = posts.filter(title__icontains=search) | posts.filter(description__icontains=search)
        max_page = posts.__len__() / PAGINATION_LIMIT
        max_page = round(max_page) + 1 if round(max_page) < max_page else round(max_page)
        print(max_page)
        posts = posts[PAGINATION_LIMIT * (page - 1):PAGINATION_LIMIT * page]
        context = {
            'posts': posts,
            'user': request.user,
            'pages': range(1, max_page + 1)

        }
        return render(request, self.template_name, context=context)


class PostDetailCBV(DetailView, CreateView):
    model = Post
    template_name = 'products/detail.html'
    form_class = ReviewCreateForm
    pk_url_kwarg = 'id'
    def get_context_data(self, *, object_list=None, **kwargs):
        return{
            'post': self.get_object(),
            'reviews': Review.objects.filter(post=self.get_object()),
            'form': kwargs.get('form', self.form_class)
        }
    def post(self, request, **kwargs):
        data=request.POST
        form = ReviewCreateForm(data=data)
        if form.is_valid():
            Review.objects.create(
                text=form.cleaned_data.get('text'),
                post_id=self.get_object().id
            )

            return render(request, self.template_name, context=self.get_context_data(form=form))

class PostCreateCBV(ListView, CreateView):
    model = Post
    template_name = 'products/create.html'
    form_class = PostCreateForm

    def get_context_data(self, *, object_list=None, **kwargs):
        return {
            'form': kwargs['form'] if kwargs.get('form') else self.form_class
        }


    def get(self, request, **kwargs):
        return render(request, self.template_name, context=self.get_context_data())
    def post(self, request, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            self.model.objects.create(
                title=form.cleaned_data.get('title'),
                description=form.cleaned_data.get('description'),
                rate=form.cleaned_data.get('rate'),
                image=form.cleaned_data.get('image')
            )
            return redirect('/products/')

        return render(request, self.template_name, context=self.get_context_data(form=form))
