from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Listing, Contact

# --- 1. PROPERTY DETAIL VIEW ---
def listing(request, listing_id):
    listing_obj = get_object_or_404(Listing, pk=listing_id)
    context = {'listing': listing_obj}
    return render(request, 'listings/listing.html', context)

# --- 2. CONTACT INQUIRY LOGIC ---
def contact(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        listing_title = request.POST['listing']
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        user_id = request.POST['user_id']

        # SPAM CHECK: If user is logged in, check if they already made an inquiry
        if request.user.is_authenticated:
            user_id = request.user.id
            has_contacted = Contact.objects.all().filter(listing_id=listing_id, user_id=user_id)
            if has_contacted:
                messages.error(request, 'You have already made an inquiry for this listing.')
                return redirect('listing', listing_id=listing_id)

        # Save to database
        contact_obj = Contact(
            listing=listing_title, listing_id=listing_id, name=name, 
            email=email, phone=phone, message=message, user_id=user_id
        )
        contact_obj.save()

        # Feedback to the user
        messages.success(request, 'Your inquiry has been submitted! A representative will contact you shortly.')
        return redirect('listing', listing_id=listing_id)

# --- 3. CREATE LISTING VIEW ---
# listings/views.py

class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    # REMOVED 'is_published' from this list
    fields = [
        'title', 'category', 'realtor_phone', 'address', 'city', 'state', 'zipcode', 
        'description', 'expectations', 'price', 'bond', 'bedrooms', 'bathrooms', 
        'is_pet_friendly', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 
        'eligibility_criteria'
    ]
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.realtor = self.request.user
        # FORCE DRAFT STATUS: Only Admin/Payment can change this later
        form.instance.is_published = False 
        messages.success(self.request, 'Listing created! Payment is required before publishing.')
        return super().form_valid(form)

class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    # REMOVED 'is_published' from here too
    fields = [
        'title', 'category', 'realtor_phone', 'address', 'city', 'state', 'zipcode', 
        'description', 'expectations', 'price', 'bond', 'bedrooms', 'bathrooms', 
        'is_pet_friendly', 'photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 
        'eligibility_criteria'
    ]
    template_name = 'listings/listing_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # If they edit it, keep it unpublished until reviewed again (Optional safety)
        form.instance.is_published = False
        messages.info(self.request, 'Listing updated. It is now pending review.')
        return super().form_valid(form)

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.realtor

# --- 5. DELETE LISTING VIEW ---
class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = 'listings/listing_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.realtor

    def delete(self, request, *args, **kwargs):
        # Changed to success message for better UX
        messages.success(self.request, "The listing has been permanently removed.")
        return super().delete(request, *args, **kwargs)


def search(request):
    queryset_list = Listing.objects.order_by('-list_date')

    # 1. Keywords (Description)
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(description__icontains=keywords)

    # 2. City
    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            queryset_list = queryset_list.filter(city__iexact=city)

    # 3. Max Price
    if 'price' in request.GET:
        price = request.GET['price']
        if price:
            queryset_list = queryset_list.filter(price__lte=price)

    # 4. NEW: Realtor Search (Agent Name)
    if 'realtor' in request.GET:
        realtor_name = request.GET['realtor']
        if realtor_name:
            # Checks if the search text is inside the First Name OR Last Name
            queryset_list = queryset_list.filter(
                Q(realtor__first_name__icontains=realtor_name) | 
                Q(realtor__last_name__icontains=realtor_name)
            )

    context = {
        'listings': queryset_list,
        'values': request.GET # Preserves search terms in the input boxes
    }
    return render(request, 'listings/search.html', context)