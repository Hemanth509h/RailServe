// Simple Dropdown navigation functionality without keyboard navigation
document.addEventListener('DOMContentLoaded', function() {
    const userDropdown = document.getElementById('userDropdown');
    const userDropdownMenu = document.getElementById('userDropdownMenu');

    if (userDropdown && userDropdownMenu) {
        // Simple open/close functions
        function openDropdown() {
            userDropdownMenu.classList.add('show');
        }

        function closeDropdown() {
            userDropdownMenu.classList.remove('show');
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

        // Close dropdown when clicking on dropdown items
        const dropdownItems = userDropdownMenu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach((item) => {
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
    }
});