function addToCart(itemId, bookingId, restaurantId) {
    const quantity = document.getElementById(`qty-${itemId}`).value;
    
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch('/food/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `item_id=${itemId}&quantity=${quantity}&booking_id=${bookingId}&restaurant_id=${restaurantId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart count
            document.getElementById('cart-count').textContent = data.item_count;
            
            // Show success message
            const btn = event.target.closest('.add-to-cart-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i>';
            btn.classList.add('btn-success');
            btn.classList.remove('btn-primary');
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.classList.add('btn-primary');
                btn.classList.remove('btn-success');
            }, 1000);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding item to cart');
    });
}