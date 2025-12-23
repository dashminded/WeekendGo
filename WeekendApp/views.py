from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import *
from django.views import View
from .forms import *
import uuid



# Create your views here.
@login_required(login_url='/login/')
def home(request):
    print("View loaded!")
    p=pg.objects.all()
    latest_pg=pg.objects.all().order_by('-id')[:2]
    o=owner.objects.all()
    f=feedback.objects.all()

    if request.GET.get('search'):
        print(request.GET.get('search'))
        p=pg.objects.filter(pg_name__icontains=request.GET.get('search'))

    for i in p:
        print(i.id, i.pg_name)


    context = {

        'p': p,
        'o': o,
        'f': f,
        'latest_pg': latest_pg
    }
    return render(request, "home.html", context)

@login_required(login_url='/login/')
def about(request):
    return render(request,'about.html')
@login_required(login_url='/login/')
def owners(request):
    p= pg.objects.all()
    context={
        'p':p
    }
    return render(request,'owners.html',context)

@login_required(login_url='/login/')
def feedback_view(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')  # Get feedback from the form
        if feedback_text:  # Ensure feedback is not empty
            f=feedback.objects.create(user=request.user, feedback=feedback_text)
            f.save()
            return render(request, 'thank_you.html')  # Redirect to a thank-you page
    return render(request, 'feedback.html')  # Render the feedback form

@login_required(login_url='/login/')
def pgs(request):
    print("View loaded!")
    p = pg.objects.all()

    if request.GET.get('search'):
        print(request.GET.get('search'))
        p = pg.objects.filter(pg_name__icontains=request.GET.get('search'))


    for i in p:
        print(i.id, i.pg_name)
    context={
        'p':p
    }
    return render(request,'pg.html',context)


@login_required(login_url='/login/')
def singlepg(request, pg_id,):
    p = get_object_or_404(pg, id=pg_id)  # Use get_object_or_404 to fetch the PG
    hostel = pg.objects.only("amenities").get(id=pg_id)

    amenities = hostel.amenities
    if amenities:
        amenities_list = amenities.split(",")  # Split amenities by commas
    else:
        amenities_list = []

    context = {
        'p': p,
        'amenities_list': amenities_list,  # Pass the amenities list to the template
    }
    return render(request, 'singlepg.html', context)

def signup(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        uname = data.get('username')
        fname = data.get('first_name')
        lname = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        print(uname, fname, lname, email, password)
        u = User.objects.filter(username=uname)
        if u.exists():
            messages.info(request, 'username already exists')
            return redirect('/signup/')
        user = User.objects.create_user(username=uname,
                                        first_name=fname,
                                        last_name=lname,
                                        email=email,
                                        )
        user.set_password(password)
        user.save()
        auth_user = authenticate(username=uname, password=password)
        if auth_user is not None:
            login(request, auth_user)
            messages.info(request, 'User registered successfully')
            return redirect('/home/')

        messages.error(request, 'Authentication failed. Please log in manually.')
        return redirect('/login/')

    return render(request, 'signup.html')


def Login(request):
    if request.method == 'POST':
        data = request.POST
        uname = data.get('username')
        password = data.get('password')
        print(uname, password)
        if not User.objects.filter(username=uname).exists():
            messages.error(request, 'Invalid username')
            return redirect('/login/')

        else:
            u = authenticate(username=uname, password=password)
            if u is None:
                messages.error(request, 'password is Invalid')
                return redirect('/login/')
            else:
                login(request, u)
                return redirect('/home/')

    return render(request, 'login.html')

def Logout(request):
    logout(request)
    return redirect('/home/')




# @login_required(login_url='/login/')
# def feedback_thank_you(request):
#     return render(request, 'thank_you.html')
# @login_required(login_url='/login/')
# def paymentdone(request):
#     return render(request, 'paymentdone.html')
# @login_required(login_url='/login/')
# def pgbooked(request):
#     return render(request, 'pgbooked.html')

@login_required(login_url='/login/')
def add_to_bookmarks(request, pg_id):
    # Get the 'pg' to be bookmarked
    pg_to_bookmark = get_object_or_404(pg, id=pg_id)

    # Check if the user has already bookmarked this 'pg'
    if not bookmark.objects.filter(user=request.user, pg=pg_to_bookmark).exists():
        bookmark.objects.create(user=request.user, pg=pg_to_bookmark)

    return redirect('/bookmarks/')  # Redirect to the bookmarks page


@login_required(login_url='/login/')
def remove_from_bookmark(request, bookmark_id):
    if request.method == "POST":
        bookmark_instance = get_object_or_404(bookmark, id=bookmark_id, user=request.user)
    # Call the remove_pg method
        bookmark_instance.remove_pg()
        bookmark_instance.delete()
        return JsonResponse({'success': True})  # Respond with JSON
    return JsonResponse({'success': False}, status=400)
    #return redirect('/bookmarks/')

@login_required(login_url='/login/')
def user_bookmarks(request):
    # Fetch all bookmarks for the logged-in user
    bookmarks = bookmark.objects.filter(user=request.user).select_related('pg')
    return render(request, 'bookmarks.html', {'bookmarks': bookmarks})




def booking_success(request):
    return render(request, "booking_success.html")





@login_required(login_url='/login/')
def book_pg(request, pg_id):
    selected_pg = get_object_or_404(pg, id=pg_id)

    if request.method == "POST":
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        if check_in and check_out:
            from datetime import datetime

            # Convert to datetime
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

            # Calculate days (minimum 1 day)
            days = (check_out_date - check_in_date).days
            if days < 1:
                days = 1

            # Calculate total amount
            total_amount = days * selected_pg.rent

            # Save booking
            booking = Booking.objects.create(
                user=request.user,
                pg=selected_pg,
                check_in=check_in_date,
                check_out=check_out_date,
                amount=total_amount
            )

            return render(request, "booking_success.html", {"booking": booking})

    return render(request, "booking_form.html", {
        "pg": selected_pg,
        "rent": selected_pg.rent,
    })



@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'my_booking.html', {'bookings': bookings})




from django.shortcuts import render
from .models import pg

from django.shortcuts import render
from .models import pg

from django.shortcuts import render
from .models import pg

def villa_list(request):
    villas = pg.objects.all()

    # Get filter values
    location = request.GET.get("location")
    min_rent = request.GET.get("min_rent")
    max_rent = request.GET.get("max_rent")
    beds = request.GET.get("beds")
    baths = request.GET.get("baths")
    search = request.GET.get("search")

    # Apply filters only if they exist
    if location:
        villas = villas.filter(location__icontains=location)
    if min_rent:
        villas = villas.filter(rent__gte=int(min_rent))
    if max_rent:
        villas = villas.filter(rent__lte=int(max_rent))
    if beds:
        villas = villas.filter(beds=int(beds))
    if baths:
        villas = villas.filter(baths=int(baths))
    if search:
        villas = villas.filter(pg_name__icontains=search)

    return render(request, "pg.html", {"p": villas})



@user_passes_test(lambda u: u.is_superuser)
def custom_admin_dashboard(request):
    # --- Sentiment Analysis ---
    sentiment_counts = feedback.objects.values("sentiment").annotate(count=Count("id"))
    sentiment_data = {item["sentiment"]: item["count"] for item in sentiment_counts}

    # --- Monthly Sales (Bookings) ---
    monthly_sales = (
        Booking.objects.annotate(month=ExtractMonth("check_in"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    monthly_data = {f"Month {item['month']}": float(item["total"]) for item in monthly_sales}

    # --- Yearly Sales (Bookings) ---
    yearly_sales = (
        Booking.objects.annotate(year=ExtractYear("check_in"))
        .values("year")
        .annotate(total=Sum("amount"))
        .order_by("year")
    )
    yearly_data = {str(item["year"]): float(item["total"]) for item in yearly_sales}
    # --- Bookings Over Time (Counts) ---
    bookings_over_time = (
        Booking.objects.annotate(month=ExtractMonth("check_in"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    bookings_data = {f"Month {item['month']}": item["count"] for item in bookings_over_time}

    # --- Top PGs by Revenue ---
    top_pgs = (
        Booking.objects.values("pg__pg_name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )
    top_pgs_data = {item["pg__pg_name"]: float(item["total"]) for item in top_pgs}

    # --- Booking Duration Distribution ---
    duration_data = []
    for booking in Booking.objects.all():
        if booking.check_in and booking.check_out:
            duration = (booking.check_out - booking.check_in).days
            if duration > 0:
                duration_data.append(duration)

    # --- Repeat Customers ---
    repeat_customers = (
        Booking.objects.values("user__username")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )
    repeat_data = {
        item["user__username"]: item["count"] for item in repeat_customers
    }

    context = {
        "sentiment_data": json.dumps(sentiment_data),
        "monthly_sales": json.dumps(monthly_data),
        "yearly_sales": json.dumps(yearly_data),
        "bookings_data": json.dumps(bookings_data),
        "top_pgs_data": json.dumps(top_pgs_data),
        "duration_data": json.dumps(duration_data),
        "repeat_data": json.dumps(repeat_data),
    }
    return render(request, "admin_dashboard.html", context)


def recommend_place(request):
    location = request.GET.get("location", "").strip()

    if location:
        recommended_pgs = pg.objects.filter(location__icontains=location).order_by("rent")[:3]
    else:
        recommended_pgs = pg.objects.order_by("rent")[:3]

    if recommended_pgs:
        data = [
            {
                "name": p.pg_name,
                "location": p.location,
                "rent": p.rent,
                "amenities": p.amenities,
            }
            for p in recommended_pgs
        ]
    else:
        data = {"error": f"No recommendations found for {location}" if location else "No recommendations available."}

    return JsonResponse(data, safe=False)





from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from .models import Booking


def generate_receipt(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Booking_Receipt_{booking.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # =============================
    # HEADER
    # =============================
    p.setFillColor(colors.red)
    p.setFont("Helvetica-Bold", 22)
    p.drawString(180, height - 80, "WeekendGo")

    p.setStrokeColor(colors.grey)
    p.setLineWidth(1)
    p.line(50, height - 90, width - 50, height - 90)

    # =============================
    # CUSTOMER + BOOKING INFO
    # =============================
    y = height - 130
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(60, y, "Guest Details:")
    y -= 25
    p.setFont("Helvetica", 12)
    p.drawString(80, y, f"Name: {booking.user.username}")
    y -= 20
    p.drawString(80, y, f"Booking ID: {booking.id}")
    y -= 20
    p.drawString(80, y, f"PG / Villa Name: {booking.pg.pg_name}")
    y -= 20
    p.drawString(80, y, f"Location: {booking.pg.location}")
    y -= 20
    p.drawString(80, y, f"Check-in Date: {booking.check_in}")
    y -= 20
    p.drawString(80, y, f"Check-out Date: {booking.check_out}")

    # =============================
    # PAYMENT SECTION (boxed)
    # =============================
    y -= 40
    p.setFillColor(colors.red)
    p.rect(60, y - 40, width - 120, 70, stroke=0, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(80, y + 15, "Payment Summary")
    p.setFont("Helvetica", 12)
    p.drawString(80, y - 5, f"Rent per day: Rs.{booking.pg.rent}")
    p.drawString(300, y - 5, f"Total Amount Paid: Rs.{booking.amount}")

    # =============================
    # EMERGENCY CONTACTS
    # =============================
    y -= 80
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(60, y, "Emergency Contacts:")
    y -= 25
    p.setFont("Helvetica", 12)
    p.drawString(80, y, f"Nearest Police Station: {'Navrangpura Police Station' or 'N/A'}")
    y -= 20
    p.drawString(80, y, f"Nearest Hospital: {'Sterling Hospital'or 'N/A'}")

    # =============================
    # OWNER DETAILS (optional)
    # =============================
    y -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(60, y, "Owner Information:")
    y -= 25
    p.setFont("Helvetica", 12)
    p.drawString(80, y, f"Owner Name: {booking.pg.owner.owner_name}")
    y -= 20
    p.drawString(80, y, f"Contact Number: {booking.pg.owner.number}")

    # =============================
    # FOOTER
    # =============================
    p.setStrokeColor(colors.grey)
    p.line(50, 100, width - 50, 100)

    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(colors.darkgray)
    p.drawString(180, 80, "Thank you for booking with us! Have a safe and pleasant stay 🏡")

    p.showPage()
    p.save()
    return response



from django.shortcuts import render, redirect, get_object_or_404


def manage_data(request):
    return render(request, "admin/manage_data.html")


# ---------------- OWNER CRUD ----------------

def owner_list(request):
    owners = owner.objects.all()
    return render(request, "admin/owner_list.html", {"owners": owners})


def owner_create(request):
    if request.method == "POST":
        form = ownerform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("owner_list")
    else:
        form = ownerform()
    return render(request, "admin/owner_form.html", {"form": form})


def owner_update(request, id):
    own = get_object_or_404(owner, id=id)
    if request.method == "POST":
        form = ownerform(request.POST, request.FILES, instance=own)
        if form.is_valid():
            form.save()
            return redirect("owner_list")
    else:
        form = ownerform(instance=own)
    return render(request, "admin/owner_form.html", {"form": form})


def owner_delete(request, id):
    own = get_object_or_404(owner, id=id)
    if request.method == "POST":
        own.delete()
        return redirect("owner_list")
    return render(request, "admin/owner_delete.html", {"owner": own})


# ---------------- PG CRUD ----------------

def pg_list(request):
    pgs = pg.objects.select_related("owner").all()
    return render(request, "admin/pg_list.html", {"pgs": pgs})


def pg_create(request):
    if request.method == "POST":
        form = pgform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("pg_list")
    else:
        form = pgform()
    return render(request, "admin/pg_form.html", {"form": form})


def pg_update(request, id):
    hostel = get_object_or_404(pg, id=id)
    if request.method == "POST":
        form = pgform(request.POST, request.FILES, instance=hostel)
        if form.is_valid():
            form.save()
            return redirect("pg_list")
    else:
        form = pgform(instance=hostel)
    return render(request, "admin/pg_form.html", {"form": form})


def pg_delete(request, id):
    hostel = get_object_or_404(pg, id=id)
    if request.method == "POST":
        hostel.delete()
        return redirect("pg_list")
    return render(request, "admin/pg_delete.html", {"pg": hostel})







