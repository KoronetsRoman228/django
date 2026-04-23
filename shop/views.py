from django.shortcuts import render


def get_pages():
    return [
        {'id': 1, 'name': 'Сторінка 1', 'path': '/page/1/'},
        {'id': 2, 'name': 'Сторінка 2', 'path': '/page/2/'},
        {'id': 3, 'name': 'Сторінка 3', 'path': '/page/3/'},
    ]


def main(request):
    context = {
        'title': 'Головна сторінка',
        'message': 'Це головна сторінка. Оберіть одну з інших сторінок нижче.',
        'pages': get_pages(),
        'is_main': True,
    }
    return render(request, 'shop/main.html', context)


def page(request, page_id):
    page_title = f'Сторінка {page_id}'
    context = {
        'title': page_title,
        'message': f'Ви зараз на {page_title}. Натисніть, щоб повернутися на головну.',
        'pages': get_pages(),
        'is_main': False,
    }
    return render(request, 'shop/main.html', context)
