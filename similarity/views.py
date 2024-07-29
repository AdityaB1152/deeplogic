from django.shortcuts import render, redirect , get_object_or_404
from .utility import extract_text_from_pdf, convert_pdf_to_image, generate_file_hash,calculate_text_similarity, calculate_structral_similarity, calculate_combined_similarity
from .forms import InvoiceUploadForm
from .models import Invoice
from django.contrib import messages

def upload_invoice(request):
    if request.method == 'POST':
        form = InvoiceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                invoice = form.save(commit=False)
                # Generate hash to check for duplicates
                invoice.hash = generate_file_hash(invoice.pdf.path)
                if Invoice.objects.filter(hash=invoice.hash).exists():
                    messages.error(request, 'This invoice already exists.')
                    return redirect('upload_invoice')
                invoice.text = extract_text_from_pdf(invoice.pdf.path)
                invoice.image_path = convert_pdf_to_image(invoice.pdf.path)
                invoice.save()
                messages.success(request, 'Invoice uploaded and processed successfully.')
                return redirect('result', invoice_id=invoice.id)
            except Exception as e:
                messages.error(request, f'Error processing invoice: {str(e)}')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = InvoiceUploadForm()
    return render(request, 'similarity/upload.html', {'form': form})



def result(request , invoice_id):
    new_invoice = get_object_or_404(Invoice, id=invoice_id)

    if Invoice.objects.exclude(id=invoice_id).count() == 0:
        return render(request , 'similarity/result.html',{
            'new_invoice':new_invoice,
            'best_match':None,
            'similarity_score':None,
            'message':'This is the first uploaded invoice. No comparison can be made yet.'
        })
    
    best_match , best_score = None,0
    for invoice in Invoice.objects.exclude(id=invoice_id):
        try:
            text_sim = calculate_text_similarity(new_invoice.text , invoice.text)
            structre_sim = calculate_structral_similarity(new_invoice.image_path , invoice.image_path)
            combined_sim = calculate_combined_similarity(text_sim , structre_sim)
            if combined_sim > best_score :
                best_score = combined_sim
                best_match = invoice
        except Exception as e :
            messages.error(request, f'Error comparing invoices: {str(e)}')


    return render(request, 'similarity/result.html' , {
        'new_invoice':new_invoice,
        'best_match':best_match,
        'similarity_score':best_score
    })