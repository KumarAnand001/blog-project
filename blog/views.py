from django.shortcuts import render, get_object_or_404
from blog.models import Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView
from django.core.mail import send_mail
from blog.forms import EmailSendForm, CommentForm

# Create your views here.
def post_list_view(request):

    post_list = Post.objects.all()
    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page')

    try:

        post_list = paginator.page(page_number)
    except PageNotAnInteger:

        post_list = paginator.page(1)
    except EmptyPage:

        post_list = paginator.page(paginator.num_pages)

    return render(request, 'blog/post_list.html', {'post_list' : post_list})

class PostListView(ListView):

    model = Post
    paginate_by = 2

def post_detail_view(request, year, month, day, slug):

    post = get_object_or_404(Post, slug = slug, status = 'published', publish__year = year,
                             
                             publish__month = month, publish__day = day)
    
    comments = post.comment.filter(active = True)
    csubmit = False
    if request.method == 'POST':

        form = CommentForm(request.POST)
        if form.is_valid():

            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            csubmit = True
    else:

        form = CommentForm()
    
    return render(request, 'blog/post_detail.html', {'post' : post, 'form':form, 'csubmit':csubmit, 'comments':comments})

def send_mail_view(request, id):

    post = get_object_or_404(Post, id = id, status = 'published')
    sent = False
    if request.method == 'POST':

        form = EmailSendForm(request.POST)
        if form.is_valid():

            cd = form.cleaned_data
            subject = '{}({}) recomends you to read "{}"'.format(cd['name'], cd['email'], post.title)
            post_url = request.build_absolute_uri(post.get_absolute_url())
            massage = 'Read Post At : \n{} \n\n{}\'s Comments : \n{}'.format(post_url, cd['name'], cd['comments'])
            send_mail(subject, massage, 'aaccfortest09@gmail.com', [cd['to']])
            sent = True
    else:

        form = EmailSendForm()

    return render(request, 'blog/sharebymail.html', {'form':form, 'post':post, 'sent':sent})
