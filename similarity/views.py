from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Invoice
from .forms import InvoiceUploadForm
from .utility import extract_text_from_pdf, generate_file_hash, convert_pdf_to_image, calculate_structural_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def upload_invoice(request):
    if request.method == 'POST':
        form = InvoiceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                invoice = form.save(commit=False)
                invoice.pdf.name = form.cleaned_data['pdf'].name
                invoice.pdf.save(invoice.pdf.name, form.cleaned_data['pdf'])  # Save the file first
                temp_file_path = invoice.pdf.path
                invoice.text = extract_text_from_pdf(temp_file_path)
                invoice.hash = generate_file_hash(temp_file_path)

                # Convert PDF to image
                try:
                    invoice.image_path = convert_pdf_to_image(temp_file_path)
                except Exception as e:
                    invoice.image_path = None
                    messages.error(request, f'Error converting PDF to image: {str(e)}')

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

def result(request, invoice_id):
    try:
        target_invoice = Invoice.objects.get(id=invoice_id)
        target_text = target_invoice.text
        target_image_path = target_invoice.image_path

        # Extract all invoice texts from the database
        invoices = Invoice.objects.exclude(id=invoice_id)
        texts = [inv.text for inv in invoices]

        # If there are other invoices to compare
        if texts:
            texts.append(target_text)

            # Convert texts to TF-IDF vectors
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform(texts)

            # Compute cosine similarity
            cosine_similarities = cosine_similarity(vectors[-1], vectors[:-1])
            most_similar_index = int(cosine_similarities.argmax())  # Ensure the index is a Python integer

            # Get the most similar invoice
            most_similar_invoice = invoices[most_similar_index]
            most_similar_image_path = most_similar_invoice.image_path

            # Compute structural similarity if both images are available
            structural_similarity = None
            if target_image_path and most_similar_image_path:
                try:
                    structural_similarity = calculate_structural_similarity(target_image_path, most_similar_image_path)
                except Exception as e:
                    messages.error(request, f'Error calculating structural similarity: {str(e)}')

            context = {
                'target_invoice': target_invoice,
                'most_similar_invoice': most_similar_invoice,
                'similarity_score': cosine_similarities[0, most_similar_index],
                'structural_similarity': structural_similarity
            }
            return render(request, 'similarity/result.html', context)
        else:
            messages.warning(request, 'No other invoices to compare with.')
            return redirect('upload_invoice')

    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('upload_invoice')
    except Exception as e:
        messages.error(request, f'Error processing similarity: {str(e)}')
        return redirect('upload_invoice')
