import json
import os
import re
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from ECom.PostActions.login import loginCheck
from ECom.forms import ImageUploadForm
from ECom.models import Address, AdminUsers, Cart, Category, Checkout, Country, Product, Users
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.contrib.auth.hashers import make_password
from commerceE import settings
from reportlab.pdfgen import canvas

# Create your views here.

def index(request):
    return render(request, "index.html", {"active": "index"})



def login(request):
    if request.method == 'POST':
        result = loginCheck(request.POST.get("username"), request.POST.get("password"), request)
        if result != "admin" and result != "user":
            return render(request, "login.html", {"result": result})
        else:
            return redirect("/profile")
    else:
        user_id = request.session.get('user_id')
        if user_id:
            user_username = request.session.get('user_username')
            if AdminUsers.objects.filter(username=user_username).exists():
                return redirect('/AuthHome')
            else:
                return redirect('/profile')
        else:
            return render(request, "login.html")
        

def register(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        user_name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        data = {
                'name': name,
                'username':user_name,
                'email':email
        }
        if (name and email and user_name and password):
            if AdminUsers.objects.filter(username=user_name).exists() or Users.objects.filter(username=user_name).exists():
                del data['username']
                return render(request, "register.html", {"result": "0", "message": "Username exists", "data": data})
            else:
                if AdminUsers.objects.filter(email=email).exists() or Users.objects.filter(email=email).exists():
                    del data['email']
                    return render(request, "register.html", {"result": "0", "message": "Email id exists", "data": data})
                else:
                    hashed_password = make_password(password)
                    users = Users.objects.create(
                        name = name,
                        username = user_name,
                        email = email,
                        password = hashed_password
                    )
                    users.save()
                    return render(request, "register.html", {"result": "1", "message": "Successful, proceed to login"})
        else:
            return render(request, "register.html", {"result": "0", "message": "Error !! please enter all fields ", "data": data})
    else:
        return render(request, "register.html")
    


def AuthHome(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'Admin/Home.html')
    else:
        print("No session present")
        return redirect('/login')



def AdminAddProduct(request):
    context = {}
    context["categories"] = Category.objects.all()

    if request.method == "POST":
        product = request.POST.get("product", "").strip()
        description = request.POST.get("description", "").strip()
        price = request.POST.get("price", "").strip()
        category_id = request.POST.get("category", "").strip()
        long_description = request.POST.get("longDescription", "").strip()
        image = request.FILES.get('image')
        

        if not (product and description and price and category_id and price.isdigit() and category_id.isdigit() and long_description and image):
            context["result"] = "Please fill in all fields and select an image"
            context["code"] = "2"
            return render(request, "Admin/AddProduct.html", context)

        try:
            category_instance = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            context["result"] = "Invalid category selected"
            context["code"] = "2"
            return render(request, "Admin/AddProduct.html", context)

        form = ImageUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            context["result"] = "Select a valid image"
            context["code"] = "2"
            return render(request, "Admin/AddProduct.html", context)

        fs = FileSystemStorage(location='media/images')
        new_filename = generate_unique_filename(image.name)
        final_filename = get_unique_filename(fs, new_filename)
        filename = fs.save(final_filename, image)

        product_model = Product.objects.create(
            name=product,
            category=category_instance,
            image=filename,
            price=int(price),
            description=description,
            longDescription= long_description
        )

        product_model.save()

        context["result"] = "Product added successfully"
        context["code"] = "1"
        return render(request, "Admin/AddProduct.html", context)

    return render(request, "Admin/AddProduct.html", context)

    



def generate_unique_filename(filename):
    extension = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{extension}"
    return new_filename

def get_unique_filename(fs, filename):
    if fs.exists(filename):
        base, ext = os.path.splitext(filename)
        index = 1
        new_filename = f"{base}_{index}{ext}"
        while fs.exists(new_filename):
            index += 1
            new_filename = f"{base}_{index}{ext}"
        return new_filename
    else:
        return filename



def AddCategory(request):
    if request.method == 'POST':
        category = request.POST.get("category")
        if category.strip() == "":
            return render(request, "Admin/AddCategory.html", {"result": "Invalid Category"})
        else:
            categoryModel = Category(name = category)
            categoryModel.save()
            return render(request, "Admin/AddCategory.html", {"result": "Category Added"})
    else:
        return render(request, "Admin/AddCategory.html")
    


def viewCategory(request):
    items = Category.objects.all()  
    paginator = Paginator(items, 5) 
    delid = request.GET.get('did')

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if delid != None:
        try:
            category_to_delete = Category.objects.get(id= delid)
            category_to_delete.delete()
            return render(request, "Admin/viewCategory.html",{'page_obj': page_obj, "del": "1"})
        except:
            return render(request, "Admin/viewCategory.html",{'page_obj': page_obj, "del": "2"})
    else:
        return render(request, "Admin/viewCategory.html",{'page_obj': page_obj})
    

def AdAllProduct(request):
    items = Product.objects.all()  
    paginator = Paginator(items, 10) 
    delid = request.GET.get('did')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if delid != None:
        try:
            product_to_delete = Product.objects.get(id= delid)
            product_to_delete.delete()
            return render(request, "Admin/ViewProducts.html",{'page_obj': page_obj, "del": "1"})
        except:
            return render(request, "Admin/ViewProducts.html",{'page_obj': page_obj, "del": "2"})
    else:
        return render(request, "Admin/ViewProducts.html",{'page_obj': page_obj})


def productOne(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        id_param = body_data.get('id')
        
        try:
            product = Product.objects.get(id=id_param)
            prod = {
                'name': product.name,
                'image': product.image,
                'id': product.id,
                'description': product.description,
                'price': product.price,
            }
            return JsonResponse({"product": prod})
        
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
    
    else:
        return JsonResponse({}, status=405)  
    

def AdminSiteHome(request):
    return render(request, "Admin/AdminSiteHome.html")
    

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('/login')





#Shop


def shop(request):
    search = request.GET.get("search")
    
    if search:
        items = Product.objects.filter(name__icontains=search)
    else:
        items = Product.objects.all()

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "shop.html", {'page_obj': page_obj})



def shopProduct(request):
    search = request.GET.get("search")
    if search:
        try:
            product = Product.objects.get(id= search)
            category_name = product.category.name 
            prod = {
                    'name': product.name,
                    'image': product.image,
                    'id': product.id,
                    'description': product.description,
                    'price': product.price,
                    'category': category_name,
                    'long_description': product.longDescription,
            }


            if request.method == 'POST':
                userId = request.session.get("user_id")
                if userId:
                    if Cart.objects.filter(user=userId, product=search).exists():
                        return render(request, "shopProduct.html", {"product": prod, "result": ["0","Product already exists in cart"]})
                    else:
                        cart = Cart.objects.create(
                            user = Users.objects.get(id = userId),
                            product = Product.objects.get(id = search),
                            count = 1
                            )
                        cart.save()
                        return render(request, "shopProduct.html", {"product": prod, "result": ["1","Item added to cart"]})
            
            else:
                return render(request, "shopProduct.html", {"product": prod})
            
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
    else:
        return redirect("/shop")
    

def profile(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_username = request.session.get('user_username')
        if AdminUsers.objects.filter(username=user_username).exists():
            return render(request, "profile.html", {"model": popupModel })
        else:
            user = Users.objects.get(id = user_id)
            log_user = {
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'phone': user.phone
            }
            return render(request, "profile.html", {'user': log_user})
    else:
        return redirect('/login')
    

def address(request):
    userId = request.session.get('user_id')
    country = Country.objects.all()
    if userId:
        if Address.objects.filter(user=userId).exists():
            address_model = Address.objects.get(user=userId)
            user_country = Country.objects.get(pk= address_model.country.id)
            country_user = {
                'id': user_country.id,
                'name': user_country.name 
            }
        else:
            country_user = {}
            address_model = {}


        if request.method == 'POST':
            selected_country = request.POST.get("country")
            state = request.POST.get("state")
            address = request.POST.get("address")
            postal = request.POST.get("postal")
            city = request.POST.get("city")
            if (selected_country and state and address and postal and city):
                if Address.objects.filter(user=userId).exists():
                    address_model.country = Country.objects.get(pk=selected_country)
                    address_model.state = state
                    address_model.city = city
                    address_model.postal = postal

                    print(selected_country)

                    address_model.save()
                    return render(request, "address.html", {"country": country, "result": "1", "message": "Update Successful", "address": address_model,"country_user":country_user})

                else:
                    address_model = Address.objects.create(
                        country = Country.objects.get(pk= selected_country),
                        state = state,
                        address=address,
                        city = city,
                        user = Users.objects.get(pk = userId),
                        postal = postal
                    )
                    address_model.save()
                    return render(request, "address.html",{ "country":country, "result": "1", "message": "Update Successfull","address": address_model, "country_user":country_user})
            else:
                return render(request, "address.html",{ "country":country, "result": "0", "message": "Error !! cannot Add or update your Address","address": address_model, "country_user":country_user})
        else:
            return render(request, "address.html",{ "country":country,"address": address_model, "country_user":country_user})
    else:
        return redirect('/login')
    


def cart(request):
    userId = request.session.get("user_id")
    if userId:
        deletion = request.GET.get("delid")
        if deletion:
            deleteItem = Cart.objects.get(
                user = Users.objects.get(pk=userId),
                product = Product.objects.get(id=deletion)
                )
            deleteItem.delete()
            return redirect("/cart")
        else:
            if Cart.objects.filter(user=userId).exists():
                cartItems = Cart.objects.filter(user=userId)
                return render(request, "cart.html", {"result":[1, cartItems]})
            else:
                return render(request, "cart.html", {"result": [1]} )       
    else:
        return redirect("/login")



def checkout(request):
    userId = request.session.get("user_id")

    if Address.objects.filter(user=userId).exists():
        address = Address.objects.get(user = userId)
    else:
        address = {}
    if userId:
        if Cart.objects.filter(user=userId).exists():
            cartItems = Cart.objects.filter(user=userId)
            total = 0
            for item in cartItems:
                total += item.product.price
            
            if request.method == 'POST':
                number = request.POST.get("card_number").strip()
                name = request.POST.get("card_name").strip()
                expiry = request.POST.get("expiry_date").strip()
                cvv = request.POST.get("cvv").strip()

                expiry_regex = r'^(0[1-9]|1[0-2])\/?([0-9]{2})$'
                cvv_regex = r'^[0-9]{3,4}$'
                card_number_regex = r'^[0-9]{16}$'

                if not name or not number.isdigit() or not re.match(expiry_regex, expiry) or not re.match(cvv_regex, cvv) or not re.match(card_number_regex, number):
                    return render(request, "checkout.html", {
                        "total": total, 
                        "data": cartItems, 
                        "result": "0", 
                        "message": "Invalid payment details"
                    })
                else:
                    cart = Cart.objects.filter(user=userId)
                    itemId = []
                    if cart.exists():
                        itemId = [cart_item.product.id for cart_item in cart]

                    for id in itemId:
                        checkout = Checkout.objects.create(
                            user=Users.objects.get(pk=userId),
                            product=Product.objects.get(pk=id),
                            count=1
                        )
                        checkout.save()
                    cart.delete()
                    request.session['booking'] = "true"
                    return redirect("/order-placed")
            else:
                return render(request, "checkout.html", {"total": total, "data": cartItems, "address": address})
        else:
            return redirect("/cart")
    else:
        return redirect("/login")
    

def order(request):
    if request.session.get("booking"):
        del request.session["booking"]
        return render(request, "paymentSuccess.html")
    else:
        return redirect("/shop")



def trackOrder(request):
    userId = request.session.get("user_id")
    if userId:
        booking = Checkout.objects.filter(user = userId)
        return render(request, "trackOrder.html", {"booking": booking})
    else:
        return redirect("/login")

def popupModel():
    return '''
        <div class="modal fade" id="messageModal" tabindex="-1" aria-labelledby="messageModalLabel" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="messageModalLabel">Message</h5>
                    </div>
                    <div class="modal-body">
                        You are Logged in as Admin
                    </div>
                    <div class="modal-footer">
                        <a href="/login" class="btn btn-primary">Continue to dashboard</a>
                        <a href="/Add-logout" class="btn btn-primary">Cancel</a>
                    </div>
                    <p class="text-center text-danger">Note, canceling will remove the login details stored</p>
                </div>
            </div>
        </div>

        <script>
        document.addEventListener('DOMContentLoaded', function() {
            var messageModal = new bootstrap.Modal(document.getElementById('messageModal'));
            messageModal.show();

            var cancelButton = document.querySelector('#messageModal .btn-primary');
            cancelButton.addEventListener('click', function() {
                messageModal.hide();
            });
        });
        </script>
    '''


def generate_invoice(request):

    id = request.GET.get("search")
    if id:
        item = Checkout.objects.get(id = id)
        address = Address.objects.get(user = request.session.get("user_id"))

        invoice_number = item.id 
        price = item.product.price

        print(price)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="invoice_{invoice_number}.pdf"'

        p = canvas.Canvas(response)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Invoice")
        p.drawString(100, 780, f"Invoice Number: {invoice_number}")

        p.setFont("Helvetica", 12)
        p.drawString(100, 760, f"Customer: {item.user.name}")
        p.drawString(100, 740, f"Date: {item.created_at.strftime('%Y-%m-%d')}")
        p.drawString(100, 720, f"Time: {item.created_at.strftime('%H:%M:%S')}")


        p.line(100, 710, 500, 710)

        yaxis = 680

        p.drawString(100, yaxis-20, "Delivery Address:")
        p.drawString(100, yaxis-40, f"{address.address}")
        p.drawString(100, yaxis-60, f"{address.city} {address.state}, ")
        p.drawString(100, yaxis-80, f"{address.postal}")
        p.drawString(100, yaxis-100, f"{address.country.name}")

        p.line(100, yaxis-110, 500, yaxis-110)


        p.drawString(100, yaxis-140, "Product:")
        p.drawString(100, yaxis-160, f"Name: {item.product.name}")
        p.drawString(100, yaxis-180, f"Description: {item.product.description}, ")



        p.drawString(100, 460, "Item")
        p.drawString(200, 460, "Quantity")
        p.drawString(300, 460, "Price")
        p.drawString(400, 460, "Total")

        items = [
            (item.product.name, str(item.count), "$ " + str(item.product.price),  "$ " +  str(item.product.price)),
        ]

        y = 430
        for item in items:
            p.drawString(100, y, item[0])
            p.drawString(200, y, item[1])
            p.drawString(300, y, item[2])
            p.drawString(400, y, item[3])
            y -= 20

        p.line(100, y, 500, y)

        p.drawString(370, y - 20, f"Total: $ {price}")

        p.drawString(100, 60, "ComE.com")
        p.line(100, 50, 500, 50)
        p.showPage()
        p.save()

        return response
    else:
        return redirect("/profile")
