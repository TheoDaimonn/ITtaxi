# ITtaxi
It project provided by Moscow Aviation Institute

#Как работать с проектом?

В папке app у нас находятся основные файлы - routes, forms, models, init, utils. Не думаю, что здесь нужно что-то пояснять - это общепринятые названия для файлов с путями(ссылками), формами, моделями, инициализации, утилиты(декораторы для стандартных функций). 

#Пройдусь по главным моментам которые могут быть непонятны, и что я вообще тут натворил по сравнению с тем, что валяется в main.

Первое - в файле models.py появилась эта штука:


  <pre>@login.user_loader

  def load_user(id):
    
      driver = Driver.query.get(int(id))
    
      if driver:
        
          return driver
    
      return User.query.get(int(id))</pre>

если коротко - она нужна для дележки пользователей и таксистов. Когда мы осуществляем вход в наше приложение, то данные пользователя подгружаются в current_user, но у нас их два вида в двух разных таблицах. Мы сначала пробуем подгрузить его из такси, а затем из юзеров. Здесь возникает конфликт - если у нас есть таксист и юзер с одинаковым id, то будет конфликт. Этот конфликт решается вот этой штукой в файле routes.py в driver_register:

<pre>
        max_id = db.session.query(func.max(Driver.id)).scalar() or 0
        new_id = 1 + max_id
        driver.id = new_id
</pre>

С помощью этой штуки мы вводим индексацию водителей с 1000000. Просто вся индексация в таблице Driver будет начинаться с миллиона, а вообще можно выставить любое число. Берется максимальный id водителя из таблицы, к нему прибавляется единица и получается следующий id в таблице.

#Что за файл utils.py?

В нем у нас лежит декоратор для стандартной функции login_required. Мы добавляем ей возможность определять "роль" пользователя чтобы доступ к определенной странице был только у пользователя с определенной ролью. 
<pre>def login_required(role):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('choice'))

            if current_user.role != role:
                print(f"Пользователь {current_user.email} имеет роль {current_user.role}, а ожидалось {role}")
                return abort(403)
            print(f"Пользователь {current_user.email} имеет роль {current_user.role}, а ожидалось {role}")

            return func(*args, **kwargs)

        return decorated_view

    return wrapper</pre>

Обертке wrapper передается наша функция, декоратором wraps сохраняются данные о вошедшем пользователе, затем вместо исполнения нашей изначальной функции func(которая и определяла право просмотра) у нас исполняется decorated_view которая проверяет роль пользователя. Если пользователю нельзя просмотреть страницу - случается ошибка доступа 403.


#Как и в какой степени реализована связь Пользователь-Заказ-Водитель?

На данный момент мы имеем следующее: На странице index которая является стандартной для пользователя отображается список сделанных им заказов, а так же имеется кнопка для совершения нового заказа. Новый заказ определяется точкой старта, финиша, временем и ценой(на данном этапе это randint). Со стороны водителя же имеется возможность перехода по адресу orders, где отображаются все заказы не имеющие исполнителя. При нажатии кнопки возле заказа, он автоматически присваивается исполнителю(т.е водителю, под логином которого мы зашли). 

<pre>@app.route('/orders')
@login_required('driver')
def show_orders():
    orders = Order.query.filter_by(driver_id=None).all()
    return render_template('orders.html', orders=orders)


@app.route('/take_order/<int:order_id>', methods=['POST'])
@login_required('driver')
def take_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.driver_id is not None:
        flash('This order has already been taken.', 'warning')
        return redirect(url_for('show_orders'))
    order.driver_id = current_user.id
    db.session.commit()
    flash('Order taken successfully!', 'success')
    return redirect(url_for('show_orders'))</pre>

В /orders отображается список заказов, затем при нажатии на заказ нас выбрасывает на страницу, где происходит вся магия присвоения заказа исполннителю незримо для нас, а затем обратная переадресация на список заказов. 
Соответственно все необходимые темплейты были в минимальном и крайне скудном виде реализованы и добавлены в templates. При тестировании учтите, что на страницу orders можно перейти только вручную.
