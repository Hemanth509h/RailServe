// Enhanced Dropdown navigation functionality with accessibility
document.addEventListener('DOMContentLoaded', function() {
    const userDropdown = document.getElementById('userDropdown');
    const userDropdownMenu = document.getElementById('userDropdownMenu');

    if (userDropdown && userDropdownMenu) {
        // Initialize ARIA attributes
        userDropdown.setAttribute('role', 'button');
        userDropdown.setAttribute('aria-haspopup', 'true');
        userDropdown.setAttribute('aria-expanded', 'false');
        userDropdown.setAttribute('tabindex', '0');
        
        userDropdownMenu.setAttribute('role', 'menu');
        userDropdownMenu.setAttribute('aria-hidden', 'true');
        
        // Add role and tabindex to dropdown items
        const dropdownItems = userDropdownMenu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach((item, index) => {
            item.setAttribute('role', 'menuitem');
            item.setAttribute('tabindex', '-1');
        });

        let currentFocusIndex = -1;

        function openDropdown() {
            userDropdownMenu.classList.add('show');
            userDropdown.setAttribute('aria-expanded', 'true');
            userDropdownMenu.setAttribute('aria-hidden', 'false');
            currentFocusIndex = -1;
            
            // Focus first item
            if (dropdownItems.length > 0) {
                currentFocusIndex = 0;
                dropdownItems[0].focus();
            }
        }

        function closeDropdown() {
            userDropdownMenu.classList.remove('show');
            userDropdown.setAttribute('aria-expanded', 'false');
            userDropdownMenu.setAttribute('aria-hidden', 'true');
            currentFocusIndex = -1;
            userDropdown.focus();
        }

        function focusNextItem() {
            if (currentFocusIndex < dropdownItems.length - 1) {
                currentFocusIndex++;
                dropdownItems[currentFocusIndex].focus();
            }
        }

        function focusPrevItem() {
            if (currentFocusIndex > 0) {
                currentFocusIndex--;
                dropdownItems[currentFocusIndex].focus();
            }
        }

        // Toggle dropdown on click
        userDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (userDropdownMenu.classList.contains('show')) {
                closeDropdown();
            } else {
                openDropdown();
            }
        });

        // Keyboard navigation for dropdown toggle
        userDropdown.addEventListener('keydown', function(e) {
            switch (e.key) {
                case 'Enter':
                case ' ':
                case 'ArrowDown':
                    e.preventDefault();
                    if (!userDropdownMenu.classList.contains('show')) {
                        openDropdown();
                    }
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (!userDropdownMenu.classList.contains('show')) {
                        openDropdown();
                        if (dropdownItems.length > 0) {
                            currentFocusIndex = dropdownItems.length - 1;
                            dropdownItems[currentFocusIndex].focus();
                        }
                    }
                    break;
                case 'Escape':
                    if (userDropdownMenu.classList.contains('show')) {
                        closeDropdown();
                    }
                    break;
            }
        });

        // Keyboard navigation within dropdown
        userDropdownMenu.addEventListener('keydown', function(e) {
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    focusNextItem();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    focusPrevItem();
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (dropdownItems[currentFocusIndex]) {
                        dropdownItems[currentFocusIndex].click();
                    }
                    break;
                case 'Escape':
                    e.preventDefault();
                    closeDropdown();
                    break;
                case 'Home':
                    e.preventDefault();
                    if (dropdownItems.length > 0) {
                        currentFocusIndex = 0;
                        dropdownItems[0].focus();
                    }
                    break;
                case 'End':
                    e.preventDefault();
                    if (dropdownItems.length > 0) {
                        currentFocusIndex = dropdownItems.length - 1;
                        dropdownItems[currentFocusIndex].focus();
                    }
                    break;
            }
        });

        // Update focus index when items are focused directly
        dropdownItems.forEach((item, index) => {
            item.addEventListener('focus', function() {
                currentFocusIndex = index;
            });
            
            item.addEventListener('click', function() {
                closeDropdown();
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                closeDropdown();
            }
        });

        // Close dropdown when focus leaves the component
        document.addEventListener('focusin', function(e) {
            if (!userDropdown.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                if (userDropdownMenu.classList.contains('show')) {
                    closeDropdown();
                }
            }
        });

        // Close dropdown when pressing Escape anywhere
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && userDropdownMenu.classList.contains('show')) {
                closeDropdown();
            }
        });
    }
});