
    document.addEventListener('DOMContentLoaded', function() {
        const quickPetSpeciesSelect = document.getElementById('quick_pet_species');
        const quickPetBreedInput = document.getElementById('quick_pet_breed');
        const quickRegForm = document.getElementById('quickRegForm');

        if (quickPetBreedInput) {
            const tomSelect = new TomSelect(quickPetBreedInput, {
                create: true,
                maxItems: 1,
                placeholder: 'ระบุสายพันธุ์...',
                createFilter: function(input) {
                    input = input.trim();
                    if(input.length === 0) return false;
                    const regex = /^[a-zA-Zก-๙0-9\s]+$/;
                    return regex.test(input);
                },
                render: {
                    option_create: function(data, escape) {
                        return '<div class="create text-success fw-bold p-2"><i class="fas fa-plus me-1"></i> + ใช้สายพันธุ์ใหม่: <strong>' + escape(data.input) + '</strong></div>';
                    },
                    no_results: function(data, escape) {
                        return '<div class="no-results p-2 text-muted small">ไม่พบสายพันธุ์ในระบบ พิมพ์ต่อเพื่อเพิ่มใหม่</div>';
                    }
                },
                onChange: function(value) {
                    const tsControl = quickPetBreedInput.parentElement.querySelector('.ts-control');
                    if (value && value.trim() !== '') {
                        tsControl.classList.remove('is-invalid', 'border-danger');
                        tsControl.classList.add('is-valid', 'border-success');
                        tsControl.style.borderWidth = '2px';
                    } else {
                        tsControl.classList.remove('is-valid', 'border-success');
                    }
                }
            });

            // Function to load breeds based on selected species
            const loadBreeds = (speciesName) => {
                tomSelect.clearOptions();
                tomSelect.clear();
                
                if (speciesName) {
                    fetch(`/ajax/get-breeds/?species=${encodeURIComponent(speciesName)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.breeds && data.breeds.length > 0) {
                                const newOptions = data.breeds.map(breed => ({ value: breed, text: breed }));
                                tomSelect.addOptions(newOptions);
                            }
                        })
                        .catch(err => console.error('Error fetching breeds:', err));
                }
            };

            if (quickPetSpeciesSelect) {
                quickPetSpeciesSelect.addEventListener('change', function(e) {
                    loadBreeds(e.target.value);
                });
            }
        }

        // Intercept form submission to apply atomic validation constraint
        if(quickRegForm) {
            quickRegForm.addEventListener('submit', function(e) {
                // Ensure species and breed are not empty
                const speciesVal = quickPetSpeciesSelect ? quickPetSpeciesSelect.value : '';
                const breedVal = quickPetBreedInput ? quickPetBreedInput.value : '';
                
                if (!speciesVal || !breedVal || breedVal.trim() === '') {
                    e.preventDefault();
                    Swal.fire({
                        icon: 'warning',
                        title: 'ข้อมูลไม่ครบถ้วน',
                        text: 'กรุณาระบุรายละเอียด "ประเภทสัตว์" และ "สายพันธุ์" ให้ครบถ้วน'
                    });
                    
                    const tsControl = quickPetBreedInput.parentElement.querySelector('.ts-control');
                    if(tsControl && (!breedVal || breedVal.trim() === '')) {
                        tsControl.classList.add('is-invalid', 'border-danger');
                        tsControl.style.borderWidth = '2px';
                    }
                } else {
                    // Trim value before submitting for data integrity
                    quickRegForm.querySelector('input[name="pet_breed"]').value = breedVal.trim();
                }
            });
        }
    });

    // 0. Primary Management Functions (High priority)
    function executeDatabaseCleanup() {
        // Close modal first
        const modalEl = document.getElementById('confirmCleanupModal');
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) modalInstance.hide();

        const daysInput = document.getElementById('cleanup_days');
        const days = daysInput ? daysInput.value : 30;
        const container = document.getElementById('cleanup_result_container');
        
        // Find CSRF token manually if needed, or use a general one
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        if (container) container.innerHTML = '<div class="alert alert-info py-2 small"><i class="fas fa-spinner fa-spin me-2"></i> กำลังลบข้อมูล Log เก่า...</div>';
        
        const formData = new URLSearchParams();
        formData.append('days_old', days);
        
        fetch("djangoTag", {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded', 
                'X-CSRFToken': csrfToken, 
                'X-Requested-With': 'XMLHttpRequest' 
            },
            body: formData.toString()
        })
        .then(response => response.json())
        .then(json => {
            if(json.success) {
                if (container) container.innerHTML = `<div class="alert alert-success py-2 small animate__animated animate__fadeIn"><i class="fas fa-check-circle me-2"></i> ${json.message}</div>`;
            } else {
                if (container) container.innerHTML = `<div class="alert alert-danger py-2 small"><i class="fas fa-times-circle me-2"></i> ${json.error}</div>`;
            }
        })
        .catch(err => {
            if (container) container.innerHTML = `<div class="alert alert-danger py-2 small"><i class="fas fa-exclamation-triangle me-2"></i> Error: ${err.message}</div>`;
        });
    }

    // Legacy Aliases
    function triggerDatabaseCleanup() { executeDatabaseCleanup(); }
    function runDatabaseCleanup() { executeDatabaseCleanup(); }

    // Initialize tooltips (Safe mode)
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    } catch(e) { console.warn("Tooltips failed to init:", e); }

    // 1. Centralized Event Listener for Dashboard Actions
    document.addEventListener('click', function(e) {
        // Edit Phone Button
        let phoneBtn = e.target.closest('.edit-phone-btn');
        if (phoneBtn) {
            const ownerId = phoneBtn.getAttribute('data-owner-id');
            const ownerName = phoneBtn.getAttribute('data-owner-name');
            const currentPhone = phoneBtn.getAttribute('data-phone');
            const resultId = phoneBtn.getAttribute('data-result-id');

            document.getElementById('modalOwnerName').innerText = ownerName + " (ID: " + ownerId + ")";
            document.getElementById('modalPhoneInput').value = currentPhone;
            document.getElementById('modalResultElId').value = resultId;
            document.getElementById('editPhoneModal').setAttribute('data-target-id', ownerId);
            
            new bootstrap.Modal(document.getElementById('editPhoneModal')).show();
            return;
        }

        // Edit Pet Button
        let petBtn = e.target.closest('.edit-pet-btn');
        if (petBtn) {
            const petId = petBtn.getAttribute('data-pet-id');
            const petName = petBtn.getAttribute('data-pet-name');
            const resultId = petBtn.getAttribute('data-result-id');

            document.getElementById('modalPetID').innerText = petId;
            document.getElementById('modalPetNameInput').value = petName;
            document.getElementById('modalPetResultElId').value = resultId;
            document.getElementById('editPetModal').setAttribute('data-target-id', petId);
            
            new bootstrap.Modal(document.getElementById('editPetModal')).show();
            return;
        }

        // Refresh Age Button
        let ageBtn = e.target.closest('.refresh-age-btn');
        if (ageBtn) {
            const func = ageBtn.getAttribute('data-func');
            const birthDate = ageBtn.getAttribute('data-birth-date');
            const resultId = ageBtn.getAttribute('data-result-id');
            executeScalar(func, {birth_date: birthDate}, resultId);
            return;
        }

        // Save Stock Button
        let stockBtn = e.target.closest('.save-stock-btn');
        if (stockBtn) {
            const medId = stockBtn.getAttribute('data-medicine-id');
            updateStockAJAX(medId);
            return;
        }
        // Edit Vet Button
        let vetBtn = e.target.closest('.edit-vet-btn');
        if (vetBtn) {
            const vetId = vetBtn.getAttribute('data-vet-id');
            const currentHours = vetBtn.getAttribute('data-hours');
            const resultId = vetBtn.getAttribute('data-result-id');

            document.getElementById('modalVetID').value = vetId;
            document.getElementById('modalVetIDDisplay').innerText = "รหัสสัตวแพทย์: " + vetId;
            document.getElementById('modalVetHoursInput').value = currentHours;
            document.getElementById('modalVetResultElId').value = resultId;
            
            new bootstrap.Modal(document.getElementById('editVetHoursModal')).show();
            return;
        }

        // Cleanup Button (Maintenance) - Handled by Modal + executeDatabaseCleanup()

        // Revenue Report Button
        let revenueBtn = e.target.closest('#runRevenueBtn');
        if (revenueBtn) {
            runRevenueReport();
            return;
        }

        // Save Vet Hours Button (Modal)
        let saveVetBtn = e.target.closest('#saveVetHoursBtn');
        if (saveVetBtn) {
            saveVetHoursUpdate();
            return;
        }
    });

    function filterInventoryTable() {
        const filter = document.getElementById("inventorySearchInput").value.toLowerCase();
        document.querySelectorAll(".inventory-row").forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.indexOf(filter) > -1 ? "" : "none";
        });
    }

    // 2. Specialized Filters (Called directly or via input)

    // 3. Core functions for Dashboard Actions
    function savePhoneUpdate() {
        const ownerId = document.getElementById('editPhoneModal').getAttribute('data-target-id');
        const newPhone = document.getElementById('modalPhoneInput').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        console.log("Saving phone update for OwnerID:", ownerId, "New Phone:", newPhone);
        if(!ownerId) { alert("Error: No OwnerID selected"); return; }

        const formData = new URLSearchParams();
        formData.append('func_name', 'update_phone_via_view');
        formData.append('owner_id', ownerId);
        formData.append('new_phone', newPhone);

        fetch("djangoTag", {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) { location.reload(); } 
            else { alert("Error: " + data.error); }
        })
        .catch(err => alert("Connection error"));
    }

    function savePetUpdate() {
        const petId = document.getElementById('editPetModal').getAttribute('data-target-id');
        const newName = document.getElementById('modalPetNameInput').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        console.log("Saving pet name update for PetID:", petId, "New Name:", newName);
        if(!petId) { alert("Error: No PetID selected"); return; }

        const formData = new URLSearchParams();
        formData.append('func_name', 'update_pet_name_via_view');
        formData.append('pet_id', petId);
        formData.append('new_pet_name', newName);

        fetch("djangoTag", {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) { location.reload(); } 
            else { alert("Error: " + data.error); }
        })
        .catch(err => alert("Connection error"));
    }

    function saveVetHoursUpdate() {
        const vetId = document.getElementById('modalVetID').value;
        const newHours = document.getElementById('modalVetHoursInput').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const formData = new URLSearchParams();
        formData.append('func_name', 'update_vet_hours_via_view');
        formData.append('vet_id', vetId);
        formData.append('new_hours', newHours);

        fetch("djangoTag", {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) { location.reload(); } 
            else { alert("Error: " + data.error); }
        })
        .catch(err => alert("Connection error"));
    }

    function executeScalar(funcName, data, resultElId) {
        const resEl = document.getElementById(resultElId);
        if(!resEl) return;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new URLSearchParams();
        formData.append('func_name', funcName);
        for(let key in data) formData.append(key, data[key]);

        resEl.innerHTML = '<span class="spinner-border spinner-border-sm text-muted"></span>';
        
        fetch("djangoTag", {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken },
            body: formData.toString()
        })
        .then(response => response.json())
        .then(json => {
            if(json.success) {
                let displayResult = json.result || '0';
                if(funcName.includes('Value') || funcName.includes('Spending') || funcName.includes('Revenue')) {
                    const num = parseFloat(displayResult.toString().replace(/,/g, ''));
                    if (!isNaN(num)) {
                        displayResult = '฿' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                    } else if (!displayResult.toString().includes('฿')) {
                        displayResult = '฿' + displayResult;
                    }
                }
                resEl.innerHTML = displayResult;
                resEl.className = 'fw-bold text-success animate__animated animate__fadeIn';
            } else {
                resEl.innerHTML = 'Error';
            }
        })
        .catch(err => { resEl.innerHTML = 'Failed'; });
    }

    // Cleanup Logic Moved to Top

    function runRevenueReport() {
        const year = document.getElementById('revenue_year').value;
        const month = document.getElementById('revenue_month').value;
        const container = document.getElementById('revenue_result_container');
        
        if(!month) { alert('กรุณาระบุเดือน'); return; }
        
        container.innerHTML = '<div class="alert alert-info py-2 small"><i class="fas fa-calculator fa-spin me-2"></i> กำลังประมวลผล T-SQL...</div>';
        
        executeScalar('sp_GetMonthlyRevenue', {year: year, month: month}, 'revenue_result_container');
    }

    function updateStockAJAX(medicineId) {
        const newStock = document.getElementById('input_stock_' + medicineId).value;
        const container = document.getElementById('stock_manager_' + medicineId);
        const originalContent = container.innerHTML;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        container.innerHTML = '<i class="fas fa-spinner fa-spin text-teal"></i>';
        
        const formData = new URLSearchParams();
        formData.append('medicine_id', medicineId);
        formData.append('new_stock', newStock);

        // Timeout 8 วินาที
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        
        fetch("djangoTag", {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
            body: formData.toString(),
            signal: controller.signal
        })
        .then(response => response.json())
        .then(json => {
            clearTimeout(timeoutId);
            if(json.success) {
                container.innerHTML = '<i class="fas fa-check-circle text-success animate__animated animate__bounceIn"></i>';
                setTimeout(() => {
                    location.reload();
                }, 800);
            } else {
                alert('Error: ' + json.error);
                container.innerHTML = originalContent;
            }
        })
        .catch(err => {
            clearTimeout(timeoutId);
            const msg = err.name === 'AbortError' ? 'หมดเวลา (Timeout)' : 'เชื่อมต่อไม่ได้';
            container.innerHTML = `<span class="text-danger small"><i class="fas fa-exclamation-circle me-1"></i>${msg}</span>`;
            setTimeout(() => { container.innerHTML = originalContent; }, 3000);
        });
    }


    // 4. Filtering Functions
    function filterClinicTable() {
        const filter = document.getElementById("clinicSearchInput").value.toLowerCase();
        document.querySelectorAll(".clinic-row").forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.indexOf(filter) > -1 ? "" : "none";
        });
    }

    function filterRegistryTable() {
        const filter = document.getElementById("registrySearchInput").value.toLowerCase();
        document.querySelectorAll(".registry-row").forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.indexOf(filter) > -1 ? "" : "none";
        });
    }

    function filterMedicineList() {
        const filter = document.getElementById("medicineSearchInput").value.toLowerCase();
        document.querySelectorAll(".medicine-item-card").forEach(card => {
            const text = card.innerText.toLowerCase();
            card.style.display = text.indexOf(filter) > -1 ? "" : "none";
        });
    }

    // Auto-load values when document is ready
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(() => {
            // Initial KPIs are now pre-rendered by Django for instant load
            // Only keeping if manual refresh is needed, but removing automatic delay on load
            // executeScalar('fn_GetMedicineStockValue', {}, 'kpi_stock_value');
            // executeScalar('fn_GetTotalClinicRevenue', {}, 'kpi_total_revenue');
        }, 500);
    });

