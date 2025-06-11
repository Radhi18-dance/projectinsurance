from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth import logout,login,authenticate
import csv
from django.contrib.auth.models import User 
from django.contrib import messages
import io
from io import BytesIO
from datetime import datetime,time,timedelta
from decimal import Decimal
import chardet
from django.http import HttpResponse
import traceback
from decimal import Decimal, InvalidOperation
import re
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
import openpyxl
from difflib import get_close_matches
from openpyxl import Workbook
from difflib import get_close_matches
from django.db.models import Min, Q
from django.http import JsonResponse
from django.db.models import Sum
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncMonth
from io import TextIOWrapper
from django.db.models import OuterRef, Subquery
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password




# Create your views here.


def custom_login(request):
    msg = ""

    if request.method == 'POST':
        # Strip extra spaces
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        print("Login form submitted with:", email, password)

        # Check if user with that email exists
        user = login_tbl.objects.filter(email__iexact=email).first()

        if user:
            print("✅ User found in DB:", user.email)

            # Optional: Show password stored (for debugging plain-text password case)
            print("Stored password:", user.password)

            # Check password: either plain text or hashed
            if user.password == password or check_password(password, user.password):
                if user.block:
                    msg = "Your account is blocked. Please contact the administrator."
                    print("❌ User is blocked")
                else:
                    # Set session
                    request.session['user'] = user.email
                    print("✅ Session set for:", request.session.get('user'))

                    # Redirect based on role
                    if user.is_superuser:
                        print("Redirecting to admin dashboard")
                        return redirect('dashboard')  # change URL name if needed
                    else:
                        print("Redirecting to user dashboard")
                        return redirect('dashboard')  # or user dashboard
            else:
                msg = "Login failed. Invalid email or password."
                print("❌ Password did not match. Entered:", password)
        else:
            msg = "Login failed. Invalid email or password."
            print("❌ No user with that email.")

    return render(request, 'login.html', {'msg': msg})
def forgotpass(request):
    if request.method == 'POST':
       mail = request.POST['email']
       user = login_tbl.objects.filter(email=mail).first()
       if user:
            request.session['email'] = mail
            print("verified")
            
            return redirect('changepass') 
       else:
           print("error")

    return render(request, 'forgotpass.html')

def changepass(request):
    if request.method=='POST':
        newpass=changepassForm(request.POST)
        cuser=request.session.get('email')
        user = login_tbl.objects.filter(email=cuser).first()
        if newpass.is_valid():
            newpass=changepassForm(request.POST, instance=user)
            newpass.save()
            print("success")
            request.session.flush()
            return redirect('/')
        else:
            print(newpass.errors)
    return render(request,'changepass.html')
 

def profile(request):
    # Get the email of the logged-in user from session
    cuser = request.session.get('user')

    if not cuser:
        return redirect('/')  # redirect to login if session expired

    try:
        # Get user details from your custom user table
        data = login_tbl.objects.get(email=cuser)
    except login_tbl.DoesNotExist:
        request.session.flush()
        return redirect('dashboard')

    try:
        # ✅ Get Django's built-in User object using email
        user_obj = login_tbl.objects.get(email=cuser)
    except User.DoesNotExist:
        user_obj = None

    return render(request, 'profile.html', {
        'cuser': cuser,
        'data': data,
        'user_obj': user_obj,  # ✅ pass the Django User object
    })

def dashboard(request):
    email = request.session.get('user')
    print("Email from session:", email)

    if not email:
        return redirect('login')

    user = login_tbl.objects.filter(email__iexact=email).first()
    print("User found:", user)

    if not user:
        return redirect('login')

    is_superuser = bool(getattr(user, 'is_superuser', False))
    user_type = 'Admin User' if is_superuser else 'Regular User'

    # Get allowed permissions for the current user
    if is_superuser:
        # If superuser, allow access to all sections
        allowed_sections = [
            "All menu", "Import CSV file", "Policy-wise report", 
            "Company-wise report", "Branch-wise report", 
            "New Client report", "Product-wise report", 
            "Policy History Report-Client wise report", "Agent wise Commission report"
        ]
    else:
        allowed_sections = Permission.objects.filter(user=user,allowed=True).values_list('section_name', flat=True)
        allowed_sections = list(allowed_sections)  # Convert queryset to list

    t_user = login_tbl.objects.all()
    rows = Insurance.objects.order_by('-id')[:25]

    context = {
        'user_type': user_type,
        't_user': t_user,
        'cuser': user,
        'is_superuser': is_superuser,
        'allowed_sections': allowed_sections,
        'rows': rows
    }

    return render(request, 'dashboard.html', context)

def logoutprofile(request):
    logout(request)
    return redirect('/')
def editprofile(request,id):
    msg=""
    user=request.session.get('user')
    cuser=login_tbl.objects.get(id=id)
    if request.method=='POST':
        updatereq=profileditForm(request.POST,request.FILES,instance=cuser)
        if updatereq.is_valid():
            updatereq.save()
            print("Updated successfully...")
            msg="Updated successfully..."
            return redirect('profile')
        else:
            print(updatereq.errors)
            msg="Something went wrong...."
    return render(request,'editprofile.html',{'msg':msg,'cuser':cuser,'user':user})





def upload(request):
    if request.method == "POST":
        files = request.FILES.getlist("csv_file")

        if not files:
            messages.error(request, "Please upload at least one CSV file.")
            return redirect('upload')

        for csv_file in files:
            if not csv_file.name.endswith(".csv"):
                messages.error(request, f"{csv_file.name} is not a valid CSV file.")
                continue

            decoded_file = csv_file.read().decode('utf-8-sig')
            if not decoded_file.strip():
                messages.error(request, f"{csv_file.name} is empty.")
                continue

            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            if not reader.fieldnames:
                messages.error(request, f"{csv_file.name} has no headers or is malformed.")
                continue

            # Normalize headers
            raw_headers = reader.fieldnames
            headers = [h.strip().upper() for h in reader.fieldnames]
            reader.fieldnames = headers
            print("[DEBUG] CSV Headers:", headers)

            # Re-create reader with cleaned headers
            reader.fieldnames = raw_headers

            FIELD_MAP = {
                "Entry Date": "entry_date",
                "Client Name": "client_name",
                "Category": "category",
                "LOB (PRODUCT)": "lob_product",
                "Insurance Company": "insurance_company",
                "Location": "location",
                "Risk Date": "risk_date",
                "Expiry Date": "expiry_date",
                "Own Damage": "own_damage",
                "Third Party": "third_party",
                "Terrorism Premium": "terrorism_premium",
                "Total Premium": "total_premium",
                "Booking Code": "booking_code",
                "Agent Name": "agent_name",
                "Policy Number": "policy_number",
                "Registered Number": "registered_number",
                "Fuel Type": "fuel_type",
                "Vehicle CC": "vehicle_cc",
                "GVW": "gvw",
                "IDV of Vehicle": "idv_of_vehicle",
                "Manufacture Year": "manufacture_year",
                "NCB": "ncb",
                "Type Of Vehicle": "type_of_vehicle",
                "Policy Type": "policy_type",
                "Contact Number": "contact_number",
                "Email Id": "email_id",
                "Reference": "reference",
                "Payment Mode": "payment_mode",
                "Bank Name": "bank_name",
                "Cheque No": "cheque_no",
                "OD BROK %": "od_brok_percent",
                "TP/TERR BROK %": "tp_terr_brok_percent",
                "Total Grid": "total_grid",
                "OD BROK AMT": "od_brok_amt",
                "TP / TERR BROK AMT": "tp_terr_brok_amt",
                "Agency Comm %": "agency_comm_percent",
                "Agency Comm. - Amt ": "agency_comm_amt",
                "Deduction % ": "deduction_percent",
                "Less Amt": "less_amt",
                "Payable": "payable",
                "TIBPL Share": "tibpl_share",
                "Receivable": "receivable",
                "Paid": "paid",
            }

            uploaded_csv = UploadedCSV.objects.create(file=csv_file)
            saved_count = 0

            try:
                for i, raw_row in enumerate(reader):
                    if not any(raw_row.values()):
                        continue

                    # Normalize row keys
                    row = {k.strip(): v for k, v in raw_row.items()}

                    cleaned_row = {}
                    for csv_key, model_key in FIELD_MAP.items():
                        value = row.get(csv_key.strip())
                        cleaned_row[model_key] = value.strip() if value else None

                    if i == 0:
                        print("[DEBUG] First row mapped:", cleaned_row)
                    # Save to database
                    Insurance.objects.create(
                        uploaded_csv=uploaded_csv,
                        entry_date=parse_date(cleaned_row.get("entry_date")),
                        client_name=cleaned_row.get("client_name"),
                        category=cleaned_row.get("category"),
                        lob_product=cleaned_row.get("lob_product", "DEBUG_MISSING") or "DEBUG_MISSING",
                        insurance_company=cleaned_row.get("insurance_company"),
                        location=cleaned_row.get("location"),
                        risk_date=parse_date(cleaned_row.get("risk_date")),
                        expiry_date=parse_date(cleaned_row.get("expiry_date")),
                        own_damage=cleaned_row.get("own_damage"),
                        third_party=cleaned_row.get("third_party"),
                        terrorism_premium=cleaned_row.get("terrorism_premium") or 0,
                        total_premium=cleaned_row.get("total_premium") or 0,
                        booking_code=cleaned_row.get("booking_code"),
                        agent_name=cleaned_row.get("agent_name"),
                        policy_number=cleaned_row.get("policy_number"),
                        registered_number=cleaned_row.get("registered_number"),
                        fuel_type=cleaned_row.get("fuel_type"),
                        vehicle_cc=parse_int(cleaned_row.get("vehicle_cc"), 'vehicle_cc', row),
                        gvw=cleaned_row.get("gvw"),
                        idv_of_vehicle=cleaned_row.get("idv_of_vehicle") or 0,
                        manufacture_year=cleaned_row.get("manufacture_year"),
                        ncb=cleaned_row.get("ncb"),
                        type_of_vehicle=cleaned_row.get("type_of_vehicle"),
                        policy_type=cleaned_row.get("policy_type"),
                        contact_number=cleaned_row.get("contact_number"),
                        email_id=cleaned_row.get("email_id"),
                        reference=cleaned_row.get("reference"),
                        payment_mode=cleaned_row.get("payment_mode"),
                        bank_name=cleaned_row.get("bank_name"),
                        cheque_no=cleaned_row.get("cheque_no"),
                        od_brok_percent=clean_percentage(cleaned_row.get("od_brok_percent")) or 0,
                        tp_terr_brok_percent=clean_percentage(cleaned_row.get("tp_terr_brok_percent"), "tp_terr_brok_percent", row),
                        total_grid=cleaned_row.get("total_grid"),
                        od_brok_amt=clean_decimal(cleaned_row.get("od_brok_amt"), "od_brok_amt", row),
                        tp_terr_brok_amt=clean_decimal(cleaned_row.get("tp_terr_brok_amt"), "tp_terr_brok_amt", row),
                        agency_comm_percent=clean_percentage(cleaned_row.get("agency_comm_percent"), "agency_comm_percent", row),
                        agency_comm_amt=clean_decimal(cleaned_row.get("agency_comm_amt"), "agency_comm_amt", row),
                        deduction_percent=clean_percentage(cleaned_row.get("deduction_percent"),'deduction_percent',row) or 0,
                        less_amt=cleaned_row.get("less_amt") or 0,
                        payable=cleaned_row.get("payable") or 0,
                        tibpl_share=cleaned_row.get("tibpl_share") or 0,
                        receivable=cleaned_row.get("receivable") or 0,
                        paid=cleaned_row.get("paid") or 0,
                    )
                    saved_count += 1

                messages.success(request, f"{saved_count} records saved from {csv_file.name}.", extra_tags="csv")

            except Exception as e:
                uploaded_csv.delete()
                messages.error(request, f"Error processing {csv_file.name}: {e}")

        return redirect('upload')

    csv_list = UploadedCSV.objects.order_by('-uploaded_at')
    return render(request, "upload.html", {"csv_list": csv_list})
def clean_value(value, target_type=str):
    if value is None or value.strip().upper() in ['NULL', 'NA', '']:
        return None
    try:
        if target_type == int:
            return int(float(value))  # Handles "123.0" as well
        elif target_type == float:
            return float(value.replace('%', '').strip())
        elif target_type == datetime:
            return parse_date(value)
        return value.strip()
    except Exception:
        return None
def parse_string(value):
   return value.strip() if value and value.strip().upper() != 'NULL' else None

def view_uploaded_csv(request, csv_id):
    uploaded_csv = get_object_or_404(UploadedCSV, id=csv_id)

    file_path = uploaded_csv.file.path
    records = []
    headers = []

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:  # Notice utf-8-sig
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            print("CSV Headers:", headers)  # Debug print in terminal
            for row in reader:
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                records.append(cleaned_row)

    except Exception as e:
        print("Error reading CSV:", e)

    return render(request, 'view_csv.html', {
        'headers': headers,
        'records': records,
        'filename': uploaded_csv.file.name,
        'total': len(records),
    })



def parse_date(value):
    """
    Try to parse a date from various common formats.
    Returns a datetime.date object if successful, else None.
    """
    if not value:
        return None

    value = str(value).strip()
    if value.upper() == "NULL" or value == "":
        return None

    date_formats = [
        "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d",
        "%d.%m.%Y", "%d %b %Y", "%d %B %Y"
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    print(f"[DEBUG] Failed to parse date: '{value}' with known formats.")
    return None

def clean_decimal(value):
    """Convert strings like '25.00%' or '25.00' to Decimal."""
    if value:
        value = value.replace('%', '').strip()
        try:
            return Decimal(value) / 100 if '%' in value else Decimal(value)
        except InvalidOperation:
            return None
    return None
def parse_int(value, idx, field_name):
    try:
        if value in (None, '', 'NULL'):
            return None
        return int(value)
    except ValueError:
        print(f"⚠️ Row {idx}: Invalid {field_name}: '{value}' is not a valid integer.")
        return None
def save_log(message):
    print(message)
    UploadedCSV.objects.create(message=message)

def clean_decimal(value, idx, field_name):
    try:
        if value is None or value.strip().upper() in ('', 'NULL'):
            return None
        value = value.strip().replace(',', '')  # Remove commas like "1,000.00"
        return Decimal(value)
    except (ValueError, InvalidOperation):
        print(f"⚠️ Row {idx}: Invalid value for '{field_name}' – '{value}' is not a valid decimal. Defaulting to None.")
        return None  # You can change this to Decimal('0.00') if needed
def clean_percentage(value, field_name=None, row=None):
    try:
        if value is None or value == "":
            return 0
        return float(str(value).replace('%', '').strip())
    except Exception:
        print(f"[ERROR] Invalid percentage for {field_name}: {value} in row: {row}")
        return 0
def policy_report_view(request):
    cuser=request.session.get('user')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    policy_number_str = request.GET.get('policy_number')

    start_date = end_date = None

    # Parse dates safely
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
        if end_date_str: 
            end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()
    except ValueError as e:
        print("Date parsing error:", e)
        # You may want to set a message in the context or log error

    # Start with all policies that have entry_date
    policies = Insurance.objects.exclude(entry_date=None)

    # Filter by policy number
    if policy_number_str:
        policies = policies.filter(policy_number__icontains=policy_number_str.strip())

    # Apply date filters as needed
    if start_date and end_date:
        if start_date <= end_date:
            policies = policies.filter(entry_date__range=(start_date, end_date))
        else:
            print("Invalid date range: start_date is after end_date")
    elif start_date:
        policies = policies.filter(entry_date__gte=start_date)
    elif end_date:
        policies = policies.filter(entry_date__lte=end_date)

    # Remove duplicates based on policy number
    policies = policies.order_by('entry_date')
    seen = set()
    unique_policies = []

    for policy in policies:
        if policy.policy_number not in seen:
            seen.add(policy.policy_number)
            unique_policies.append(policy)

    context = {
        'policies': unique_policies,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'policy_number': policy_number_str,
        'cuser':cuser
    }
    return render(request, 'policy_report.html', context)
def export_policy_excel(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    company = request.GET.get("insurance_company")
    location = request.GET.get("location")
    lob_product = request.GET.get("lob_product")
    client_name = request.GET.get("client_name")
    agent_name = request.GET.get("agent_name")
    policy_number = request.GET.get("policy_number")

    # Subquery: Find earliest policy (entry_date) per client+LOB
    earliest_policy_subquery = (
        Insurance.objects
        .filter(
            client_name=OuterRef('client_name'),
            lob_product=OuterRef('lob_product'),
            
        )
        .order_by('entry_date')
        .values('pk')[:1]
        
    )
   
    # Get only first policy per (client_name, lob_product)
    policies = Insurance.objects.filter(pk__in=Subquery(earliest_policy_subquery))

    # Now apply other filters
    if start_date:
        policies = policies.filter(entry_date__gte=start_date)
    if end_date:
        policies = policies.filter(entry_date__lte=end_date)
    if company:
        policies = policies.filter(insurance_company__icontains=company)
    if location:
        policies = policies.filter(location__icontains=location)
    if lob_product:
        policies = policies.filter(lob_product__icontains=lob_product)
    if client_name:
        policies = policies.filter(client_name__icontains=client_name)
    if agent_name:
        policies = policies.filter(agent_name__icontains=agent_name)
    if policy_number:
        policies = policies.filter(policy_number__icontains=policy_number)


    # Excel export setup
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Insurance Report"

    headers = [
        "Entry Date", "Client Name", "Category", "LOB (Product)", "Insurance Company", "Location", "Risk Date",
        "Expiry Date", "Own Damage", "Third Party", "Terrorism Premium", "Total Premium", "Booking Code",
        "Agent Name", "Policy Number", "Registered Number", "Fuel Type", "Vehicle CC", "GVW", "IDV of Vehicle",
        "Manufacture Year", "NCB", "Type of Vehicle", "Policy Type", "Contact Number", "Email ID", "Reference",
        "Payment Mode", "Bank Name", "Cheque No", "OD Brok %", "TP/Terr Brok %", "Total Grid", "OD Brok Amt",
        "TP/Terr Brok Amt", "Agency Comm %", "Agency Comm Amt", "Deduction %", "Less Amt", "Payable",
        "TIBPL Share", "Receivable", "Paid"
    ]
    ws.append(headers)

    for policy in policies:
        row = [
            str(policy.entry_date or ""),
            str(policy.client_name or ""),
            str(policy.category or ""),
            str(policy.lob_product or ""),
            str(policy.insurance_company or ""),
            str(policy.location or ""),
            str(policy.risk_date or ""),
            str(policy.expiry_date or ""),
            str(policy.own_damage or ""),
            str(policy.third_party or ""),
            str(policy.terrorism_premium or ""),
            str(policy.total_premium or ""),
            str(policy.booking_code or ""),
            str(policy.agent_name or ""),
            str(policy.policy_number or ""),
            str(policy.registered_number or ""),
            str(policy.fuel_type or ""),
            str(policy.vehicle_cc or ""),
            str(policy.gvw or ""),
            str(policy.idv_of_vehicle or ""),
            str(policy.manufacture_year or ""),
            str(policy.ncb or ""),
            str(policy.type_of_vehicle or ""),
            str(policy.policy_type or ""),
            str(policy.contact_number or ""),
            str(policy.email_id or ""),
            str(policy.reference or ""),
            str(policy.payment_mode or ""),
            str(policy.bank_name or ""),
            str(policy.cheque_no or ""),
            str(policy.od_brok_percent or ""),
            str(policy.tp_terr_brok_percent or ""),
            str(policy.total_grid or ""),
            str(policy.od_brok_amt or ""),
            str(policy.tp_terr_brok_amt or ""),
            str(policy.agency_comm_percent or ""),
            str(policy.agency_comm_amt or ""),
            str(policy.deduction_percent or ""),
            str(policy.less_amt or ""),
            str(policy.payable or ""),
            str(policy.tibpl_share or ""),
            str(policy.receivable or ""),
            str(policy.paid or "")
        ]
        ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=insurance_report.xlsx"
    wb.save(response)
    return response

def get_field_value(cleaned, key):
    value = cleaned.get(key)
    if value is None:
        from difflib import get_close_matches
        match = get_close_matches(key, cleaned.keys(), n=1, cutoff=0.6)
        if match:
            print(f"🔍 Using fallback for '{key}': {match[0]}")
            value = cleaned.get(match[0])
    return value


def company_wise_report(request):
    cuser=request.session.get('user')
    form = CompanyReportForm(request.GET or None)
    report_data = Insurance.objects.all()

    if form.is_valid():
        insurance_company = form.cleaned_data.get('insurance_company')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        print(f"Filter values: insurance_company={insurance_company}, start_date={start_date}, end_date={end_date}")

        if insurance_company:
            # Use case-insensitive exact match
            report_data = report_data.filter(insurance_company__iexact=insurance_company)

        if start_date and end_date:
            report_data = report_data.filter(entry_date__range=[start_date, end_date])
        elif start_date:
            report_data = report_data.filter(entry_date__gte=start_date)
        elif end_date:
            report_data = report_data.filter(entry_date__lte=end_date)

        print(f"Filtered queryset count: {report_data.count()}")

    else:
        print("Form is not valid")
        print(form.errors)

    return render(request, 'company_report.html', {
        'form': form,
        'report_data': report_data,
        'cuser':cuser
    })

def branch_wise_report(request):
    cuser=request.session.get('user')
    form = ReportFilterForm(request.GET or None)
    records = Insurance.objects.all()

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        location = form.cleaned_data.get('location')

        if start_date:
            records = records.filter(entry_date__gte=start_date)
        if end_date:
            records = records.filter(entry_date__lte=end_date)
        if location:
            records = records.filter(location__icontains=location) # Use exact match for FK field

    return render(request, 'branch_wise.html', {
        'records': records,
        'form': form,
        'cuser':cuser
    })
def new_client_policy_report(request):
    # Filter only new policies
    cuser=request.session.get('user')
    new_policies = Insurance.objects.filter(policy_type__iexact="New")

    # Group by entry_date and count
    datewise_summary = (
        new_policies
        .values('entry_date')
        .annotate(total_new=Count('id'))
        .order_by('entry_date')
    )

    context = {
        'summary': datewise_summary,
        'policies': new_policies,
        'cuser':cuser
    }
    return render(request, 'new_client_report.html', context)
def lob_wise_date_breakup_report(request):
    cuser=request.session.get('user')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    qs = Insurance.objects.all()

    if start_date:
        qs = qs.filter(entry_date__gte=start_date)
    if end_date:
        qs = qs.filter(entry_date__lte=end_date)

    qs = qs.annotate(month=TruncMonth('entry_date'))

    report_data = qs.values('month', 'lob_product').annotate(
        total_premium_sum=Sum('total_premium')
    ).order_by('month', 'lob_product')

    data_by_month = {}
    for item in report_data:
        month = item['month'].strftime('%Y-%m-%d') if item['month'] else '' # Example: 2024-12
        lob = item['lob_product']
        total_premium = item['total_premium_sum']

        if month not in data_by_month:
            data_by_month[month] = {}
        data_by_month[month][lob] = total_premium

    all_lobs = qs.values_list('lob_product', flat=True).distinct()

    context = {
        'data_by_month': data_by_month,
        'all_lobs': sorted(set(x for x in all_lobs if x is not None)) if all_lobs else [],
        'start_date': start_date,
        'end_date': end_date,
        'cuser':cuser
    }
    return render(request, 'product_lob_wise.html', context)

def policy_history_client_wise(request):
    cuser=request.session.get('user')
    form = PolicyHistoryForm(request.GET or None)
    policies = None
    summary_by_month = None
    selected_client = None
    start_date = None
    end_date = None

    if form.is_valid():
        selected_client = form.cleaned_data['client_name']
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Start with all policies for the selected client
        policies = Insurance.objects.filter(client_name=selected_client)

        # Apply date filters only if provided
        if start_date and end_date:
            if start_date <= end_date:
                policies = policies.filter(entry_date__range=(start_date, end_date))
        elif start_date:
            policies = policies.filter(entry_date__gte=start_date)
        elif end_date:
            policies = policies.filter(entry_date__lte=end_date)

        policies = policies.order_by('entry_date')

        # Monthly summary aggregation
        summary_by_month = policies.values('entry_date__year', 'entry_date__month') \
            .annotate(
                total_premium_sum=Sum('total_premium'),
                policies_count=Count('id')
            ).order_by('entry_date__year', 'entry_date__month')

        # Annotate month for display
        for item in summary_by_month:
            year = item['entry_date__year']
            month = item['entry_date__month']
            item['month'] = f"{year}-{month:02d}-01"

    context = {
        'form': form,
        'policies': policies,
        'summary_by_month': summary_by_month,
        'selected_client': selected_client,
        'start_date': start_date,
        'end_date': end_date,
        'cuser':cuser
    }
    return render(request, 'policy_history_report.html', context)
def agent_commission_report(request):
    cuser=request.session.get('user')
    form = AgentCommissionFilterForm(request.GET or None)
    queryset = Insurance.objects.all()

    if form.is_valid():
        agent = form.cleaned_data.get('agent_name')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        client_name=form.cleaned_data.get('client_name')
        

        if agent:
            queryset = queryset.filter(agent_name=agent)
        if start_date:
            queryset = queryset.filter(entry_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(entry_date__lte=end_date)
        if client_name:
            queryset = queryset.filter(client_name__lte=client_name)
       



    # Group by date and sum commissions
    date_wise_data = queryset.values('entry_date','client_name','lob_product','od_brok_amt','tp_terr_brok_amt','policy_number','insurance_company','agent_name','payable','terrorism_premium','third_party').order_by('entry_date','client_name').annotate(
        total_commission=Sum('agency_comm_amt'),
        total_premium=Sum('total_premium'),
      
    )
    for item in date_wise_data:
        payable_total = payable_total + item['payable']
        


    context = {
        'form': form,
        'data': date_wise_data,
        'cuser':cuser,
        'payable_total': payable_total,
       
    }
    return render(request, 'agent_wise_commission_report.html', context)


def delete_uploaded_csv(request, csv_id):
    csv = get_object_or_404(UploadedCSV, pk=csv_id) 
    csv.delete()  # This will delete linked Insurance records too
    messages.success(request, "CSV and related records deleted.")
    return redirect('upload')
def export_new_client_policies_excel(request):
    # Subquery: Earliest "New" policy per client_name and lob_product
    earliest_policy_subquery = Insurance.objects.filter(
        client_name=OuterRef('client_name'),
        lob_product=OuterRef('lob_product'),
        policy_type__iexact="New"
    ).order_by('entry_date').values('pk')[:1]

    # Filter only the earliest New policies per client_name and lob_product
    policies = Insurance.objects.filter(pk__in=Subquery(earliest_policy_subquery))

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "New Client Policies"

    # Define headers (same as shown in HTML)
    headers = [
        "Entry Date", "Client Name", "Category", "LOB (Product)",
        "Insurance Company", "Location", "Risk Date", "Expiry Date",
        "Own Damage", "Third Party", "Terrorism Premium", "Total Premium"
    ]
    ws.append(headers)

    # Fill in rows
    for policy in policies:
        ws.append([
            policy.entry_date.strftime('%b %d, %Y') if policy.entry_date else "",
            policy.client_name or "",
            policy.category or "",
            policy.lob_product or "",
            policy.insurance_company or "",
            policy.location or "",
            policy.risk_date.strftime('%b %d, %Y') if policy.risk_date else "",
            policy.expiry_date.strftime('%b %d, %Y') if policy.expiry_date else "",
            float(policy.own_damage or 0),
            float(policy.third_party or 0),
            float(policy.terrorism_premium or 0),
            float(policy.total_premium or 0),
        ])

    # Return Excel response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=new_client_policies.xlsx'
    wb.save(response)
    return response
def adduser(request):
    msg = ""
    cuser = request.session.get('user')
    SECTIONS = {
        1: "All menu",
        2: "Import CSV file",
        3: "Policy-wise report",
        4: "Company-wise report",
        5: "Branch-wise report",
        6: "New Client report",
        7: "Product-wise report",
        8: "Policy History Report-Client wise report",
        9: "Agent wise Commission report",
       
    }

    if not cuser:
        return redirect('login')

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        firstname = request.POST.get('firstname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        block = request.POST.get('block') == 'on'

        if login_tbl.objects.filter(email=email).exists():
            msg = "A user with this email already exists."
        else:
            try:
                user = login_tbl.objects.create(
                    email=email,
                    firstname=firstname,
                    lastname=lastname,
                    username=username,
                    password=password,
                    block=block,
                    user_id=user_id
                )

                # Save permissions
                for i, section_name in SECTIONS.items():
                    allowed = f'allowed_{i}' in request.POST
                    block = f'block_{i}' in request.POST
                    
                    Permission.objects.create(
                        user=user,
                        section_name=section_name,
                        allowed=1 if allowed else 0,
                        block=block
                    )

                msg = "User and permissions added successfully!"

            except IntegrityError:
                msg = "Something went wrong while saving the user."

    users = login_tbl.objects.all()
    return render(request, 'adduser.html', {
        'msg': msg,
        'cuser': cuser,
        'users': users,
        'user': None,
        'sections': SECTIONS
    })

SECTIONS = {
    1: 'All menu',
    2: 'Import CSV file',
    3: 'Policy-wise report',
    4: 'Company-wise report',
    5: 'Branch-wise report',
    6: 'New Client report',
    7: 'Product-wise report',
    8: 'Policy History Report-Client wise report',
    9: 'Agent wise Commission report'
}

def edituser(request, user_id):
    cuser = request.session.get('user')
    user = login_tbl.objects.get(id=user_id)

    existing_perms = Permission.objects.filter(user=user)
    perm_dict = {perm.section_name: perm for perm in existing_perms}

    if request.method == "POST":
        user.user_id = request.POST.get('user_id')  
        user.firstname = request.POST.get('firstname')
        user.lastname = request.POST.get('lastname')
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        user.password = request.POST.get('password')
        user.block = request.POST.get('block') == 'on'
        user.save()

        for key, section in SECTIONS.items():
            allowed = request.POST.get(f'allowed_{key}') == 'on'
            block = request.POST.get(f'block_{key}') == 'on'

            perm, created = Permission.objects.get_or_create(user=user, section_name=section)
            perm.allowed = allowed
            perm.block = block
            perm.save()

        return redirect('dashboard')

    return render(request, 'edituser.html', {
        'user': user,
        'cuser': cuser,
        'sections': SECTIONS,
        'perm_data': perm_dict,
        'msg': "Editing user"
    })