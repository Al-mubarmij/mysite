from django.shortcuts import render, redirect
from .forms import EmailGeneratorForm
from .models import Store, DevEmail, EmailBody, Instructions, Marketplace, QualityResolution, Chat
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
import requests


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('emails')  # Redirect to the email generator view
        else:
            # Invalid login
            return render(request, 'email_app/login.html', {'form': request.POST, 'error': 'Invalid username or password.'})
    return render(request, 'email_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

def chat(request):
    N8N_WEBHOOK_URL = "https://monzir.app.n8n.cloud/webhook-test/a597afab-8291-4f5e-a27c-5559636d9688"


    # Proxy server
    proxies = {
        'http': 'http://proxy.server:3128',
        'https': 'http://proxy.server:3128',  # Optional, if you want to route HTTPS through the same proxy
    }

    if request.method == 'POST':
        # Get message from the request
        message = request.POST.get('message')

        # Send POST request to n8n with the chat message via proxy
        response = requests.post(N8N_WEBHOOK_URL, json={"message": message}, proxies=proxies)


    chat = Chat.objects.all()
    context = {
        'chat': chat,
    }
    return render(request, 'email_app/chat.html', context)


def email_generator(request):
    email_details = {}
    instructions = ""

    if request.method == "GET":
        form = EmailGeneratorForm(request.GET)
        if form.is_valid():
            case_type = form.cleaned_data['case_type']
            store = form.cleaned_data['store_name']
            order_id = form.cleaned_data['order_id']
            seller_email = form.cleaned_data['seller_email']
            customer_name = form.cleaned_data['customer_name']
            customer_phone = form.cleaned_data['customer_phone']
            item_name = form.cleaned_data['item_name']
            barcode = form.cleaned_data['barcode']

            email_details['from'] = 'ksa@maf.com'

            if case_type in ['missing', 'damaged', 'wrong']:
                email_details['to'] = store.team_members_emails.split(',')
                email_details['cc'] = [store.manager_email, "hal@maf.com"]
                email_details['subject'] = f"{order_id} - {store.name}"

            elif case_type in ['rotten', 'bad_smell', 'expired', 'near_expiry']:
                email_details['to'] = store.team_members_emails.split(',')
                district_manager_email = store.district.manager_email  # Retrieve the district manager
                email_details['cc'] = [store.manager_email, district_manager_email]  # Combine with store manager
                email_details['subject'] = f"{order_id} - {store.name}"
                email_details['body'] = (f"Dear Team,\n\nResolution: {form.cleaned_data['resolution']}\n"
                             f"Customer Name: {customer_name}\n"
                             f"Customer Phone: {customer_phone}\n"
                             f"Problem: {case_type}\n"
                             f"Item Name: {item_name}\n"
                             f"Barcode: {barcode}")
    else:
        form = EmailGeneratorForm()
    return render(request, 'email_app/email_generator.html', {'form': form, 'email_details': email_details, 'instructions': instructions})


@login_required
def email_generator1(request):
    email_details = {}
    instructions = ""

    if request.method == 'POST':
        form = EmailGeneratorForm(request.POST)
        if form.is_valid():
            case_type = form.cleaned_data['case_type']
            store = form.cleaned_data['store_name']
            order_id = form.cleaned_data['order_id']
            print('orderid is', order_id)
            seller_email = form.cleaned_data['seller_email']
            customer_name = form.cleaned_data['customer_name']
            customer_phone = form.cleaned_data['customer_phone']
            item_name = form.cleaned_data['item_name']
            barcode = form.cleaned_data['barcode']



            # Common from Email
            email_details['from'] = 'ksa@maf.com'

            if case_type in ['missing', 'damaged', 'wrong']:
                email_details['to'] = store.team_members_emails.split(',')
                email_details['cc'] = [store.manager_email, "hal@maf.com"]
                email_details['subject'] = f"{order_id} - {store.name}"
                print('orderid is', order_id)

            elif case_type in ['rotten', 'bad_smell', 'expired', 'near_expiry']:
                email_details['to'] = store.team_members_emails.split(',')
                district_manager_email = store.district.manager_email  # Retrieve the district manager
                email_details['cc'] = [store.manager_email, district_manager_email]  # Combine with store manager
                email_details['subject'] = f"{order_id} - {store.name}"
                email_details['body'] = (f"Dear Team,\n\nResolution: {form.cleaned_data['resolution']}\n"
                             f"Customer Name: {customer_name}\n"
                             f"Customer Phone: {customer_phone}\n"
                             f"Problem: {case_type}\n"
                             f"Item Name: {item_name}\n"
                             f"Barcode: {barcode}")
            elif case_type == 'dev':
                email_details['to'] = [dev.to_email for dev in DevEmail.objects.all()]
                email_details['cc'] = [dev.cc_email for dev in DevEmail.objects.all()]
                email_details['subject'] = f"{order_id} - {customer_name}"
                email_details['body'] = (f"Customer Name: {customer_name}\n"
                                         f"Customer Email: {seller_email}\n"
                                         f"Order ID: {order_id}")

            elif case_type in ['marketplace_seller', 'marketplace_myl', 'marketplace_arx']:
                email_details['to'] = seller_email if case_type == 'marketplace_seller' else [marketplace.to_email for marketplace in Marketplace.objects.filter(case_type=case_type)]
                email_details['cc'] = [marketplace.cc_email for marketplace in Marketplace.objects.filter(case_type=case_type)]
                email_details['subject'] = f"{order_id} - "
                email_details['body'] = EmailBody.objects.get(case_type=case_type).body

            # Get instructions
            #instructions = Instructions.objects.get(case_type=case_type).instruction

    else:
        form = EmailGeneratorForm()

    return render(request, 'email_app/email_generator.html', {'form': form, 'email_details': email_details, 'instructions': instructions})





@login_required
def emails(request):
    stores = Store.objects.all()
    resolutions = QualityResolution.objects.all()
    store_name = ""
    order_id = ""
    team_members_emails = ""
    email_output_display = "style='display: none;'"
    manager_email = ""
    email_body = ""
    case_type = ""
    item_name = ""
    barcode = ""
    customer_name = ""
    customer_phone = ""
    customer_email = ""
    quality_case = ""
    quality_to_email = ""
    quality_cc_emails = ""
    district_manager = ""
    cc = ""
    to = ""
    to_display = ''
    cc_display = ''
    subject_display = ''

    attachment_warning = ""

    mp_case = ""
    going_to = ""

    customer_case = ''

    if request.method == "POST":
        case_type = request.POST.get('case_type')
        if case_type == "store":
            store_id = request.POST.get('store_id', '1')
            order_id = request.POST.get('order_id')
            store_case = request.POST.get('store_case')
            store_name = get_object_or_404(Store, pk=store_id).name
            store_name = request.POST.get('store_name')
            email_output_display = "style='display: block;'"
            team_members_emails = get_object_or_404(Store, pk=store_id).team_members_emails
            manager_email = get_object_or_404(Store, pk=store_id).manager_email
            to = team_members_emails
            cc = manager_email + ', ' + 'halmutawah1@mafcarrefour.com'
            if store_case == "damaged" or store_case == "wrong":
                attachment_warning = "style='display: block;'"

            email_body = """Dear Store Team,

Happy Afternoon,

Kindly check the below reported complaint and share your feedback within 2 hours as per the SLA, if not, we will proceed with the refund.

            """

        elif case_type == "beh":
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            store_id = request.POST.get('store_id', '1')
            store_name = request.POST.get('store_name')
            order_id = request.POST.get('order_id')
            email_output_display = "style='display: block;'"
            manager_email = get_object_or_404(Store, pk=store_id).manager_email
            to = manager_email
            cc = "halmutawah1@mafcarrefour.com; gghaiss@mafcarrefour.com"

            email_body = f"""Dear Manager,

I hope this email finds you well,

We received a complaint from a customer



Customer's name: {customer_name}
Customer's phone number: {customer_phone}

            """

        elif case_type == "dev":
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            customer_email = request.POST.get('customer_email')
            dev_case = request.POST.get('dev_case')
            to = "dev@mafcarrefour.com"
            cc = "PArora@mafcarrefour.com; trathakrishnan@mafcarrefour.com; markhan@mafcarrefour.com; mpackirisamy@mafcarrefour.com; sjha@mafcarrefour.com; halmutawah@mafcarrefour.com"
            email_output_display = "style='display: block;'"
            if dev_case == "wallet":
                email_body = dev_wallet(customer_name, customer_email, customer_phone)
            elif dev_case == "phone":
                email_body = dev_phone(customer_name, customer_email, customer_phone)



        elif case_type == "quality":
            order_id = request.POST.get('order_id')
            print ("order id is + ", order_id)
            store_id = request.POST.get('store_id', 1)

            store_name = get_object_or_404(Store, pk=store_id).name
            resolution = request.POST.get('resolution')
            quality_case = request.POST.get('quality_case')
            item_name = request.POST.get('item_name')
            barcode = request.POST.get('barcode')
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            email_output_display = "style='display: block;'"
            team_members_emails = get_object_or_404(Store, pk=store_id).team_members_emails
            manager_email = get_object_or_404(Store, pk=store_id).manager_email
            quality_to_email = "QualityKSA@mafcarrefour.com"
            to = team_members_emails + ', ' + quality_to_email
            quality_cc_emails = "bgeagea@mafcarrefour.com, gghaiss@mafcarrefour.com, pguillien@mafcarrefour.com, Asmitshoek@mafcarrefour.com, zmasri@mafcarrefour.com,Halmutawah1@mafcarrefour.com, jjuan@mafcarrefour.com, afathy@mafcarrefour.com, Nalokla@mafcarrefour.com, mohamedkali@mafcarrefour.com, mhodhod@mafcarrefour.com, mohhafez@mafcarrefour.com,  asshahid@mafcarrefour.com"
            district_manager = get_object_or_404(Store, pk=store_id).district.manager_email
            cc = manager_email + ', ' + district_manager + ", " + quality_cc_emails
            attachment_warning = "style='display: block;'"
            email_body = f"""Dear Store/Quality,

Happy Afternoon,

Please find the below freshness complaint type received from the customer to ensure to investigate and share the corrective actions taken to avoid such in future:

{resolution}
            """
            if customer_name != "":
                email_body += f"""
Customer name: {customer_name}
Customer phone: {customer_phone}

            """
            email_body += f"""
Problem: {quality_case}
Store name: {store_name}
Order #{order_id}
Item name: {item_name}
Bar code: {barcode}
            """
        elif case_type == "marketplace":
            order_id = request.POST.get('consignment_id')
            mp_case = request.POST.get('mp_case')
            #going_to = request.POST.get('going_to')
            #period = request.POST.get('mp_period')
            email_output_display = "style='display: block;'"
            seller_email = request.POST.get('seller_email')
            item_name = request.POST.get("item_name")
            quantity = request.POST.get("quantity")
            price = request.POST.get("price")
            comment = request.POST.get("comment")
            to = seller_email
            cc = "dshahin@mafcarrefour.com; MPSellerSupportKSA@mafcarrefour.com, halmutawah1@mafcarrefour.com; gghaiss@mafcarrefour.com"

            '''
            if going_to == "seller":
                if period == "first":
                    to = seller_email
                    cc = "dshahin@mafcarrefour.com; MPSellerSupportKSA@mafcarrefour.com, halmutawah1@mafcarrefour.com"

                else:
                    to = "dshahin@mafcarrefour.com; MPSellerSupportKSA@mafcarrefour.com;  halmutawah1@mafcarrefour.com; "
                    cc = ""
            else:
                if going_to == "imile":
                    pass
                else:
                    pass
            '''

            email_body = f"""
                Dear team / seller,

                Kindly note that we have received a complaint from the customer regarding Order #{order_id[:-2]}

                Consignment ID : {order_id}
                Item: {item_name}
                unit price  : {price}
                QTY: {quantity}
                RAWB:

                Customer need : {mp_case}
                Comment :  {comment}

                Kindly investigate and update us on the action taken within 24 hours.
                If no reply from your side, we will proceed and refund the amount to the customer.
                """


        elif case_type == "customer":

            order_id = request.POST.get('order_id')
            customer_case = request.POST.get('customer_case')
            customer_language = request.POST.get('customer_language')
            if customer_case == 'image':
                email_body = pending_image(order_id, customer_language)

            elif customer_case == "activate_wallet":
                email_body = activate_wallet(order_id, customer_language)

            elif customer_case == "bank":

                email_body = get_bank(order_id, customer_language)

            elif customer_case == "refunded_wallet":
                email_body = refunded_wallet(order_id, customer_language)

            elif customer_case == "refunded_bank":
                email_body = refunded_bank(order_id, customer_language)

            elif customer_case == "clarification":
                email_body = clarification(order_id, customer_language)

            elif customer_case == "unreachable":
                email_body = unreachable(order_id, customer_language)




            email_output_display = "style='display: block;'"
            to_display = "style='display: none;'"
            cc_display = "style='display: none;'"
            subject_display = "style='display: none;'"


    cc = cc + "; mzaroug@mafcarrefour.com"
    email_body = email_body.replace('\n', '<br>')
    context = {
        'stores': stores,
        'store_name': store_name,
        'order_id': order_id,
        'email_output_display': email_output_display,
        'manager_email': manager_email,
        'email_body': email_body,
        'case_type': case_type,
        'attachment_warning': attachment_warning,
        'resolutions': resolutions,
        'to': to,
        'cc': cc,
        'to_display': to_display,
        'cc_display': cc_display,
        'subject_display': subject_display,



    }
    return render(request, 'email_app/emails.html', context )



def pending_image(order_id, customer_language):
    if customer_language == 'arabic':
        return f"""عزيزي العميل،

نأمل أن تكون بخير. نود أن نطلب منك إرسال صورة أو فيديو للمنتج التالف أو الخاطئ الذي استلمته في طلبك رقم {order_id}. سيساعدنا ذلك في معالجة المشكلة بشكل أسرع.

نشكركم على تعاونكم.

تحياتنا،
فريق خدمة عملاء كارفور
"""
    else:
        return f"""Dear Customer,

We hope this message finds you well. We would like to request that you send us an image or video of the damaged or wrong item you received for your order ID {order_id}. This will help us resolve the issue more quickly.

Thank you for your cooperation.

Best regards,
Carrefour Customer Care Team"""

def activate_wallet(order_id, customer_language):
    if customer_language == "arabic":
        return f""" عزيزنا

نود أن نطلب منك تفعيل الاسترداد الفوري في المحفظة الخاصة بك. يمكنك القيام بذلك من خلال اتباع الخطوات التالية:

افتح التطبيق
اضغط على "المزيد"
اضغط على "محفظة كارفور" ثم قم بتفعيل رد الأموال الفوري
نشكركم على تعاونكم.

تحياتنا،
فريق خدمة عملاء كارفور

"""
    else:
        return f"""
        Dear

We would like to ask you to enable the instant refund feature in your wallet. You can do this by following these steps:

Open the app
Press "More"
Press "Wallet" and enable instant refunds
Thank you for your cooperation.

Best regards,
Carrefour Customer Care Team
"""



def get_bank(order_id, customer_language):
    print('working')
    if customer_language == 'arabic':
        return f""" عزيزنا

نحتاج إلى تفاصيل حسابك البنكي لاسترداد المبلغ المتعلق بطلبك رقم {order_id}. يرجى إرسال المعلومات التالية:

IBAN
اسمك
اسم البنك
نشكركم على تعاونكم.

تحياتنا،
فريق خدمة عملاء كارفور
"""
    else:
        return f"""Dear

We need your bank account details to process the refund for your order ID {order_id}. Please provide the following information:

IBAN
Your Name
Bank Name
Thank you for your cooperation.

Best regards,
Carrefour Customer Care Team

"""


def refunded_wallet(order_id, customer_language):
    if customer_language == 'arabic':
        return f""" عزيزنا


يسعدنا إبلاغك بأنه تم استرداد المبلغ إلى محفظتك. يمكنك التحقق من رصيدك في التطبيق.

إذا كان لديك أي استفسارات، لا تتردد في التواصل معنا.

تحياتنا،
فريق خدمة عملاء كارفور

"""
    else:
        return f"""Dear

We are pleased to inform you that the amount has been refunded to your wallet. You can check your balance in the app.

If you have any questions, please do not hesitate to contact us.

Best regards,
Carrefour Customer Care Team"""



def refunded_bank(order_id, customer_language):
    if customer_language == "arabic":
        return f""" عزيزنا
مساء الخير!

نود إبلاغك بأنه تم إجراء عملية الاسترداد إلى نفس الحساب البنكي الذي تم الدفع من خلاله. يرجى ملاحظة أن المبلغ المسترد قد يستغرق من 7 إلى 14 يومًا ليظهر في حسابك بناءً على إجراءات البنك.

أطيب التحيات،
فريق خدمة العملاء في كارفور

"""
    else:
        return f"""Dear
Happy afternoon!

We wanted to inform you that your refund has been processed to the same bank account you used for the payment. Please note that the refund may take 7 to 14 days to reflect in your account, depending on your bank's procedures.

Best regards,
Carrefour Customer Care Team """

def clarification(order_id, customer_languate):
    if customer_languate == "arabic":
        return f"""
عزيزنا العميل،
مساء الخير!

.  للأسف، لم نتمكن من تحديد المشكلة من الصورة المرسلة. هل يمكنك توضيح المشكلة أو إرسال تفاصيل إضافية لنتمكن من مساعدتك بشكل أفضل؟

أطيب التحيات،
فريق خدمة العملاء في كارفور """

    else:
        return f"""Dear Customer,
Happy afternoon!

Unfortunately, we were unable to identify the issue from the provided picture. Could you please clarify the problem or share additional details to help us assist you better?

Best regards,
Carrefour Customer Care Team """

def unreachable(order_id, customer_language):
    if customer_language == "arabic":
        return f"""عزيزنا
مساء الخير!

حاولنا الاتصال بك بخصوص استفسارك الأخير، ولكن لم نتمكن من الوصول إليك. يرجى إعلامنا بالوقت المناسب للاتصال بك، أو يمكنك التواصل معنا في أي وقت يناسبك.

أطيب التحيات،
فريق خدمة العملاء في كارفور """
    else:
        return f"""Dear
Happy afternoon!

We tried to reach you by phone regarding your recent inquiry but were unable to get through. Please let us know a convenient time to call, or feel free to contact us at your earliest convenience.

Best regards,
Carrefour Customer Care Team """

def dev_wallet(name, email, phone):
    return f"""Dear Dev,

Happy Afternoon,

Kindly provide wallet ID for this customer:
Customer name: {name}
Customer email: {email}
Customer phone: {phone}

            """

def dev_phone(name, email, phone):
    return f"""Dear Dev,

Happy Afternoon,

We’ve received a complaint from a customer stating that when they try to log in, they get an error message saying "This phone number is already registered."
Kindly check and update.
Customer name: {name}
Customer email: {email}
Customer phone: {phone}
            """

