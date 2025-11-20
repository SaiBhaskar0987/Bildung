        // Function to open student details panel
        function openStudentPanel(studentId) {
            document.getElementById('studentPanel').classList.add('active');
            
            // In a real application, you would fetch student data based on studentId
            // For this demo, we're just using static data
        }

        // Function to close student details panel
        function closeStudentPanel() {
            document.getElementById('studentPanel').classList.remove('active');
        }

        // Function to toggle section content
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            section.classList.toggle('active');
        }

        // Close panel when clicking outside of it
        document.addEventListener('click', function(event) {
            const panel = document.getElementById('studentPanel');
            if (!panel.contains(event.target) && !event.target.closest('.student-card')) {
                closeStudentPanel();
            }
        });