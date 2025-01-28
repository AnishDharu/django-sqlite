from django.shortcuts import render,redirect
from django.http import HttpResponse
from AdminApp.models import Category,Product
from UserApp.models import UserInfo,MyCart,Payment,Status,Order_Master
from datetime import datetime
# Create your views here.

def home(request):
    cats = Category.objects.all()
    products = Product.objects.all() 
    return render(request,"homepage.html",{"cats":cats,"products":products})

def viewProducts(request,pid):
    cats = Category.objects.all()
    category = Category.objects.get(id=pid)
    products = Product.objects.filter(category=category)
    return render(request,'homepage.html',{"cats":cats, "products":products})

def ViewDetails(request,id):
    if(request.method=="GET"):
        cats = Category.objects.all()
        product = Product.objects.get(id=id)
        return render(request,'ViewDetails.html',{"cats":cats,"product":product})
    else:
        #User is logged in
        if "uname" in request.session:
            uname = request.session["uname"]
            user = UserInfo.objects.get(username=uname)
            product = Product.objects.get(id=request.POST["product_id"])
            status = Status.objects.get(status_name='Cart')
            quantity = request.POST["quantity"]
            #check if item already in cart
            try:
                item = MyCart.objects.get(user=user,product=product,status=status)
            except:
                #we can insert the item in cart
                item= MyCart(user=user,product=product,quantity=quantity,status=status)
                item.save()
            return redirect(showAllCartItems)        
        else:
            return redirect(login)
        
        

def showAllCartItems(request):
    if (request.method == "GET"):
        if "uname" in request.session:
            uname = request.session["uname"]
            user = UserInfo.objects.get(username=uname)
            status = Status.objects.get(status_name='Cart')
            items = MyCart.objects.filter(user=user,status=status)
            cats = Category.objects.all()
            total = 0
            for item in items:
                total += item.product.price * item.quantity
            request.session["total"] = total
            return render(request,"showAllCartItems.html",{"items":items,"cats":cats})
        else:
            return redirect(login)
    else:
        action = request.POST["action"]
        id = request.POST["item_id"]
        item = MyCart.objects.get(id=id)
        if action == "delete":
            
            item.delete()
        else:
            quantity = request.POST["quantity"]
            item.quantity = quantity
            item.save()
        return redirect(showAllCartItems)



def login(request):
    if(request.method=="GET"):
        cats = Category.objects.all()
        return render(request,"login.html",{"cats":cats})
    else:
        username = request.POST["uname"]
        password = request.POST["pwd"]
        try:
            user = UserInfo.objects.get(username=username,password=password)
        except:
            #invalid credentials
            return redirect(login)
        else:
            request.session["uname"]=username
            return redirect(home)
        
        
def register(request):
    if(request.method=="GET"):
        cats = Category.objects.all()
        return render(request,"register.html",{"cats":cats})
    else:
        username = request.POST["uname"]
        password = request.POST["pwd"]
        email = request.POST["email"]
        try:
            print(username)
            user = UserInfo.objects.get(email=email)
        except:
            #If match not found, then this user is new user
            #so we can create new user
            success_msg="Registered Successfully"
            user = UserInfo(username=username,password=password,email=email)
            user.save()
            return render(request,"register.html",{
                "success_msg":success_msg
            })
        else:
            err = "User already exists with same email !"
            return render(request,"register.html",{
                "err":err
            })
        
def logout(request):
    request.session.clear()
    return redirect(home)

def makepayment(request): 
    if request.method == "GET":
        cats = Category.objects.all()
        return render(request ,"makepayment.html",{"cats":cats})
    else:
        card_no = request.POST["card_no"]
        cvv = request.POST["cvv"]
        expiry = request.POST["expiry"]
        #check if valid
        try:
            user = Payment.objects.get(card_no=card_no,cvv=cvv,expiry=expiry)
        except:
            #return redirect(makepayment)
            error_message = "Enter Details as follows\nCard No : 111 \ncvv : 111\nExpiry : 12/2030"
            return render(request, "makepayment.html", {
               
                "error": error_message,
                "card_no": card_no,
                "cvv": cvv,
                "expiry": expiry,
            })
        else:
            #Proceed to make payment
            amount = request.session["total"]
            if(amount < user.balance):                
                user.balance -= amount
                owner = Payment.objects.get(card_no='222',cvv='222',expiry='12/2030')
                owner.balance += amount
                owner.save()
                user.save()
                #insert record in order_master
                uname = request.session["uname"]
                user = UserInfo.objects.get(username=uname)
                order = Order_Master(date_of_order=datetime.now(),amount=amount,user=user)
                order.save()
                #modify status of cart items
                status = Status.objects.get(status_name='Cart')
                items = MyCart.objects.filter(user=user,status=status)
                status1 = Status.objects.get(status_name='Order')
                
                for item in items:
                    item.status = status1
                    item.order_id = order
                    item.save()
            else:
                return HttpResponse("Insuffiecient Balance")
            return redirect(home)
        
        
        
def MyOrders(request):
    cats = Category.objects.all()
    user = UserInfo.objects.get(username = request.session["uname"])
    orders = Order_Master.objects.filter(user=user).order_by('-date_of_order')
    items={}

    for order in orders:
        items[order] = MyCart.objects.filter(order_id=order, user=user)
        
    return render(request,"MyOrder.html",{"items":items,"cats":cats})