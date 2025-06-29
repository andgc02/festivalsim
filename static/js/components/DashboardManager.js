/**
 * Dashboard Manager - Handles dashboard updates and data management
 */
class DashboardManager {
    constructor(festivalId) {
        this.festivalId = festivalId;
        this.festivalData = null;
        this.lastDataUpdate = 0;
        this.CACHE_DURATION = 5000; // 5 seconds cache
        this.chartsInitialized = false;
    }

    async loadFestivalData(forceRefresh = false) {
        try {
            // Check cache first
            const now = Date.now();
            if (!forceRefresh && this.festivalData && (now - this.lastDataUpdate) < this.CACHE_DURATION) {
                console.log('Using cached festival data');
                this.updateDashboard(this.festivalData);
                return;
            }
            
            console.log('Loading festival data...');
            const response = await fetch(`/api/festival/${this.festivalId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.festivalData = await response.json();
            this.lastDataUpdate = now;
            
            // Set global variable for pause menu
            window.currentFestivalData = this.festivalData;
            
            this.updateDashboard(this.festivalData);
            
            // Initialize charts on first load
            if (!this.chartsInitialized) {
                this.initializeCharts();
                this.chartsInitialized = true;
            }
            
            // Update charts with new data
            this.updateCharts();
            
            console.log('Festival data loaded successfully');
        } catch (error) {
            console.error('Error loading festival data:', error);
            this.showAlert('Error loading festival data: ' + error.message, 'danger');
        }
    }

    updateDashboard(data) {
        console.log('=== UPDATE DASHBOARD START ===');
        
        if (!data) {
            console.log('No data provided for dashboard update');
            return;
        }

        const festival = data.festival;
        const artists = data.artists || [];
        const vendors = data.vendors || [];
        const tickets = data.tickets || [];
        const synergies = data.synergies || [];
        const vendorRelationships = data.vendor_relationships || [];

        console.log('Step 1: Updating festival stats...');
        this.updateFestivalStats(festival, artists, vendors, tickets);
        
        console.log('Step 2: Updating days remaining...');
        this.updateDaysRemaining(festival);
        
        console.log('Step 3: Updating lists...');
        this.updateLists(artists, vendors);
        
        console.log('Step 4: Updating analytics metrics...');
        this.updateAnalyticsMetrics(festival, artists, vendors, tickets);
        
        console.log('Step 5: Updating synergies...');
        this.updateSynergies(synergies);
        
        console.log('Step 6: Updating vendor relationships...');
        this.updateVendorRelationships(vendorRelationships);
        
        console.log('Step 7: Updating sidebar components...');
        this.updateSidebarComponents(festival, artists, vendors);
        
        console.log('=== UPDATE DASHBOARD COMPLETE ===');
    }

    updateFestivalStats(festival, artists, vendors, tickets) {
        document.getElementById('budgetDisplay').textContent = this.formatCurrency(festival.current_budget || festival.budget);
        
        const ticketsSold = tickets.reduce((sum, t) => sum + (t.sold_quantity || 0), 0);
        document.getElementById('ticketsSold').textContent = this.formatNumber(ticketsSold);
        
        document.getElementById('artistsCount').textContent = artists.length;
        document.getElementById('vendorsCount').textContent = vendors.length;
    }

    updateDaysRemaining(festival) {
        const daysUntil = festival.days_remaining || 365;
        document.getElementById('daysUntilFestival').textContent = daysUntil > 0 ? daysUntil : 'Today!';
    }

    updateLists(artists, vendors) {
        this.updateArtistsList(artists);
        this.updateVendorsList(vendors);
        this.updateEventsList(artists, vendors);
    }

    updateAnalyticsMetrics(festival, artists, vendors, tickets) {
        const totalRevenue = tickets.reduce((sum, ticket) => sum + ((ticket.sold_quantity || 0) * (ticket.price || 0)), 0);
        const budgetUsed = festival.budget > 0 ? 
            ((festival.budget - (festival.current_budget || festival.budget)) / festival.budget * 100).toFixed(1) : 0;
        const avgTicketPrice = tickets.length > 0 ? 
            (totalRevenue / tickets.reduce((sum, t) => sum + (t.sold_quantity || 0), 0)).toFixed(2) : 0;
        const roi = festival.budget > 0 ? ((totalRevenue - festival.budget) / festival.budget * 100).toFixed(1) : 0;
        
        document.getElementById('totalRevenue').textContent = this.formatCurrency(totalRevenue);
        document.getElementById('budgetUsed').textContent = budgetUsed + '%';
        document.getElementById('avgTicketPrice').textContent = this.formatCurrency(avgTicketPrice);
        document.getElementById('roi').textContent = roi + '%';
        
        // Performance Metrics
        const festivalScore = this.calculateFestivalScore(festival, artists, vendors);
        const artistSatisfaction = this.calculateArtistSatisfaction(artists);
        const vendorSatisfaction = this.calculateVendorSatisfaction(vendors);
        const marketingEffectiveness = this.calculateMarketingEffectiveness(festival, artists, vendors);
        
        document.getElementById('festivalScore').textContent = festivalScore + '/100';
        document.getElementById('artistSatisfactionScore').textContent = artistSatisfaction;
        document.getElementById('vendorSatisfactionScore').textContent = vendorSatisfaction;
        document.getElementById('marketingEffectiveness').textContent = marketingEffectiveness + '%';
        
        // Operational Metrics
        const totalArtists = artists.length;
        const totalVendors = vendors.length;
        const marketing = festival.marketing && Array.isArray(festival.marketing) ? festival.marketing : [];
        const events = festival.events && Array.isArray(festival.events) ? festival.events : [];
        const activeMarketing = marketing.filter(m => m.status === 'active').length;
        const pendingEvents = events.filter(e => !e.resolved).length;
        
        document.getElementById('totalArtists').textContent = totalArtists;
        document.getElementById('totalVendors').textContent = totalVendors;
        document.getElementById('activeMarketing').textContent = activeMarketing;
        document.getElementById('pendingEvents').textContent = pendingEvents;
    }

    updateArtistsList(artists) {
        const container = document.getElementById('artistsList');
        if (artists.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No artists hired yet.</p>';
            return;
        }
        
        container.innerHTML = artists.map(artist => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <strong>${artist.name}</strong><br>
                    <small class="text-muted">${artist.genre} • Popularity: ${artist.popularity}</small>
                </div>
                <span class="badge bg-${artist.status === 'confirmed' ? 'success' : 'warning'}">${artist.status}</span>
            </div>
        `).join('');
    }

    updateVendorsList(vendors) {
        const container = document.getElementById('vendorsList');
        if (vendors.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No vendors hired yet.</p>';
            return;
        }
        
        container.innerHTML = vendors.map(vendor => {
            // Get vendor specialties if available
            let specialtiesHtml = '';
            if (vendor.vendor_specialties && vendor.vendor_specialties.length > 0) {
                specialtiesHtml = vendor.vendor_specialties.map(s => `<span class='badge bg-info me-1 small'>${s.replace('_',' ').toUpperCase()}</span>`).join(' ');
            }
            
            // Get placement
            const placement = vendor.placement_location || 'Food Court';
            
            return `
            <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${vendor.name}</strong><br>
                            <small class="text-muted">${vendor.specialty || vendor.category} • Quality: ${vendor.quality}/100</small><br>
                            <small class="text-muted">Placement: ${placement}</small>
                            ${specialtiesHtml ? `<br>${specialtiesHtml}` : ''}
                        </div>
                        <div class="ms-2">
                            <button class="btn btn-sm btn-outline-danger" onclick="fireVendor(${vendor.id})" title="Fire Vendor">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }).join('');
    }

    updateEventsList(artists, vendors) {
        const container = document.getElementById('eventsContainer');
        const unresolvedEvents = artists.concat(vendors).filter(item => !item.resolved);
        
        if (unresolvedEvents.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No events at the moment.</p>';
            return;
        }
        
        container.innerHTML = unresolvedEvents.map(event => `
            <div class="alert alert-${event.severity === 'critical' ? 'danger' : event.severity === 'warning' ? 'warning' : 'info'} mb-2">
                <h6 class="alert-heading">${event.title}</h6>
                <p class="mb-1">${event.description}</p>
                <small class="text-muted">${event.timestamp}</small>
            </div>
        `).join('');
    }

    updateSynergies(synergies) {
        const container = document.getElementById('synergiesContainer');
        if (!container) return;

        if (synergies.length === 0) {
            container.innerHTML = '<p class="text-muted">No synergies available yet. Hire more artists to unlock synergies!</p>';
            return;
        }

        const synergiesHtml = synergies.map(synergy => `
            <div class="alert alert-success mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${synergy.name}</strong>
                        <p class="mb-1 small">${synergy.description}</p>
                        <small class="text-muted">
                            Artists: ${synergy.artist_count} | 
                            Marketing Bonus: +${(synergy.marketing_bonus * 100).toFixed(0)}% | 
                            Reputation Bonus: +${synergy.reputation_bonus}
                        </small>
                    </div>
                    <span class="badge bg-success">Active</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = synergiesHtml;
    }

    updateVendorRelationships(vendorRelationships) {
        const container = document.getElementById('vendorRelationshipsContainer');
        if (!container) return;

        if (vendorRelationships.length === 0) {
            container.innerHTML = '<p class="text-muted">No vendor relationships to display. Hire more vendors to see relationships!</p>';
            return;
        }

        const relationshipsHtml = vendorRelationships.map(relationship => {
            const alertClass = relationship.type === 'complementary' ? 'alert-success' : 'alert-warning';
            const icon = relationship.type === 'complementary' ? 'fa-handshake' : 'fa-exclamation-triangle';
            
            return `
                <div class="alert ${alertClass} mb-2">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${relationship.vendor1} & ${relationship.vendor2}</strong>
                            <p class="mb-1 small">${relationship.effect}</p>
                            <small class="text-muted">Type: ${relationship.type}</small>
                        </div>
                        <i class="fas ${icon}"></i>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = relationshipsHtml;
    }

    updateSidebarComponents(festival, artists, vendors) {
        // Update events container
        this.updateEventsContainer();
        
        // Update risk assessment
        this.updateRiskAssessment(festival);
        
        // Update marketing recommendations
        this.updateMarketingRecommendations(festival);
        
        // Update approaching artists/vendors
        this.updateApproachingArtists(artists);
        this.updateApproachingVendors(vendors);
    }

    updateEventsContainer() {
        const container = document.getElementById('eventsContainer');
        if (!container) return;

        // Get events from festival data
        const events = this.festivalData?.events || [];
        
        if (events.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No events at the moment.</p>';
            return;
        }

        const eventsHtml = events.map((event, index) => {
            const severityClass = event.severity === 'positive' ? 'success' : 
                                event.severity === 'negative' ? 'danger' : 'warning';
            const severityIcon = event.severity === 'positive' ? 'fa-check-circle' : 
                               event.severity === 'negative' ? 'fa-exclamation-triangle' : 'fa-info-circle';
            
            // Generate interactive options HTML
            let optionsHtml = '';
            if (event.interactive_options && event.interactive_options.length > 0) {
                optionsHtml = `
                    <div class="mt-3">
                        <h6 class="text-muted mb-2">Choose your response:</h6>
                        <div class="d-flex flex-wrap gap-2">
                            ${event.interactive_options.map(option => `
                                <button class="btn btn-sm btn-outline-${severityClass} event-option-btn" 
                                        data-event-type="${event.type}" 
                                        data-option-id="${option.id}"
                                        data-cost="${option.cost}"
                                        title="${option.description}">
                                    ${option.label} ($${option.cost.toLocaleString()})
                                </button>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            return `
                <div class="alert alert-${severityClass} mb-3" id="event-${index}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <strong><i class="fas ${severityIcon} me-2"></i>${event.type}</strong>
                            <p class="mb-2">${event.description}</p>
                            <small class="text-muted">
                                ${event.effects ? Object.entries(event.effects).map(([key, value]) => 
                                    `${key}: ${value > 0 ? '+' : ''}${value}`
                                ).join(', ') : ''}
                            </small>
                            ${optionsHtml}
                        </div>
                        <small class="text-muted ms-2">${new Date(event.timestamp).toLocaleTimeString()}</small>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = eventsHtml;
        
        // Add event listeners for interactive options
        this.addEventOptionListeners();
    }
    
    addEventOptionListeners() {
        const optionButtons = document.querySelectorAll('.event-option-btn');
        optionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleEventResponse(button);
            });
        });
    }
    
    async handleEventResponse(button) {
        const eventType = button.dataset.eventType;
        const optionId = button.dataset.optionId;
        const cost = parseInt(button.dataset.cost);
        
        // Check if we have enough budget
        if (this.festivalData?.festival?.budget < cost) {
            this.showNotification('Insufficient budget for this action!', 'error');
            return;
        }
        
        // Disable all buttons for this event to prevent multiple clicks
        const eventContainer = button.closest('.alert');
        const allButtons = eventContainer.querySelectorAll('.event-option-btn');
        allButtons.forEach(btn => btn.disabled = true);
        
        try {
            const response = await fetch(`/api/events/respond/${this.festivalId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: eventType,
                    option_id: optionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show success message
                this.showNotification(result.message, 'success');
                
                // Update festival data
                if (this.festivalData?.festival) {
                    this.festivalData.festival.budget = result.new_budget;
                    this.festivalData.festival.reputation = result.new_reputation;
                }
                
                // Update the UI
                this.updateDashboard(this.festivalData);
                
                // Mark event as resolved
                eventContainer.classList.add('alert-success');
                eventContainer.innerHTML = `
                    <div class="d-flex align-items-center">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        <div>
                            <strong>Event Resolved</strong>
                            <p class="mb-0">${result.message}</p>
                        </div>
                    </div>
                `;
                
                // Remove event from the list after a delay
                setTimeout(() => {
                    eventContainer.remove();
                }, 3000);
                
            } else {
                this.showNotification(result.error || 'Failed to respond to event', 'error');
                // Re-enable buttons
                allButtons.forEach(btn => btn.disabled = false);
            }
            
        } catch (error) {
            console.error('Error responding to event:', error);
            this.showNotification('Error responding to event', 'error');
            // Re-enable buttons
            allButtons.forEach(btn => btn.disabled = false);
        }
    }

    updateRiskAssessment(festival) {
        const container = document.getElementById('riskAssessmentContainer');
        if (!container) return;

        // Calculate risk based on festival data
        let riskScore = 0;
        let riskLevel = 'Low';
        let riskColor = 'success';

        if (festival.budget < 20000) {
            riskScore += 30;
        }
        if (festival.reputation < 30) {
            riskScore += 25;
        }
        if (festival.days_remaining < 30) {
            riskScore += 20;
        }

        if (riskScore > 50) {
            riskLevel = 'High';
            riskColor = 'danger';
        } else if (riskScore > 25) {
            riskLevel = 'Medium';
            riskColor = 'warning';
        }

        container.innerHTML = `
            <div class="text-center">
                <div class="badge bg-${riskColor} fs-6 mb-2">${riskLevel} Risk</div>
                <div class="small text-muted">Risk Score: ${riskScore}/100</div>
                <div class="mt-2">
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-${riskColor}" style="width: ${riskScore}%"></div>
                    </div>
                </div>
            </div>
        `;
    }

    updateMarketingRecommendations(festival) {
        const container = document.getElementById('marketingRecommendationsContainer');
        if (!container) return;

        const recommendations = [];

        if (festival.reputation < 40) {
            recommendations.push('Focus on reputation-building campaigns');
        }
        if (festival.budget > 50000) {
            recommendations.push('Consider premium marketing campaigns');
        }
        if (festival.days_remaining < 60) {
            recommendations.push('Launch urgent promotional campaigns');
        }

        if (recommendations.length === 0) {
            recommendations.push('Your festival is well-positioned!');
        }

        const recommendationsHtml = recommendations.map(rec => 
            `<div class="small mb-1"><i class="fas fa-lightbulb text-warning me-1"></i>${rec}</div>`
        ).join('');

        container.innerHTML = recommendationsHtml;
    }

    updateApproachingArtists(artists) {
        const card = document.getElementById('approachingArtistsCard');
        const list = document.getElementById('approachingArtistsList');
        
        if (!card || !list) return;

        // Show card if there are artists with high popularity
        const approachingArtists = artists.filter(a => a.popularity > 80);
        
        if (approachingArtists.length > 0) {
            card.style.display = 'block';
            const artistsHtml = approachingArtists.map(artist => `
                <div class="small mb-2">
                    <strong>${artist.name}</strong> (${artist.popularity}/100)
                    <br><small class="text-muted">${artist.genre}</small>
                </div>
            `).join('');
            list.innerHTML = artistsHtml;
        } else {
            card.style.display = 'none';
        }
    }

    updateApproachingVendors(vendors) {
        const card = document.getElementById('approachingVendorsCard');
        const list = document.getElementById('approachingVendorsList');
        
        if (!card || !list) return;

        // Show card if there are vendors with high quality
        const approachingVendors = vendors.filter(v => v.quality > 85);
        
        if (approachingVendors.length > 0) {
            card.style.display = 'block';
            const vendorsHtml = approachingVendors.map(vendor => `
                <div class="small mb-2">
                    <strong>${vendor.name}</strong> (${vendor.quality}/100)
                    <br><small class="text-muted">${vendor.specialty}</small>
                </div>
            `).join('');
            list.innerHTML = vendorsHtml;
        } else {
            card.style.display = 'none';
        }
    }

    calculateFestivalScore(festival, artists, vendors) {
        let score = 0;
        
        const currentBudget = festival.current_budget || festival.budget;
        const budgetEfficiency = festival.budget > 0 ? (currentBudget / festival.budget) * 100 : 0;
        score += Math.min(budgetEfficiency, 25);
        
        if (artists.length > 0) {
            const avgArtistPopularity = artists.reduce((sum, artist) => sum + (artist.popularity || 0), 0) / artists.length;
            score += (avgArtistPopularity / 100) * 25;
        }
        
        const vendorCategories = new Set(vendors.map(v => v.category || v.type || 'unknown'));
        score += Math.min(vendorCategories.size * 5, 20);
        
        const marketing = festival.marketing && Array.isArray(festival.marketing) ? festival.marketing : [];
        const activeMarketing = marketing.filter(m => m.status === 'active');
        score += Math.min(activeMarketing.length * 5, 15);
        
        const totalTickets = artists.concat(vendors).reduce((sum, item) => sum + (item.sold_quantity || 0), 0);
        score += Math.min(totalTickets / 10, 15);
        
        return Math.round(score);
    }

    calculateArtistSatisfaction(artists) {
        if (artists.length === 0) return 'N/A';
        
        const confirmedArtists = artists.filter(a => a.status === 'confirmed');
        const satisfactionRate = (confirmedArtists.length / artists.length) * 100;
        
        if (satisfactionRate >= 90) return 'Excellent';
        if (satisfactionRate >= 75) return 'Good';
        if (satisfactionRate >= 50) return 'Fair';
        return 'Poor';
    }

    calculateVendorSatisfaction(vendors) {
        if (vendors.length === 0) return 'N/A';
        
        const confirmedVendors = vendors.filter(v => v.status === 'confirmed');
        const satisfactionRate = (confirmedVendors.length / vendors.length) * 100;
        
        if (satisfactionRate >= 90) return 'Excellent';
        if (satisfactionRate >= 75) return 'Good';
        if (satisfactionRate >= 50) return 'Fair';
        return 'Poor';
    }

    calculateMarketingEffectiveness(festival, artists, vendors) {
        const marketing = festival.marketing && Array.isArray(festival.marketing) ? festival.marketing : [];
        const activeMarketing = marketing.filter(m => m.status === 'active');
        let baseEffectiveness = 100;
        
        if (activeMarketing.length > 0) {
            const totalEffectiveness = activeMarketing.reduce((sum, campaign) => sum + (campaign.effectiveness || 0), 0);
            baseEffectiveness = Math.min(Math.round(totalEffectiveness * 100), 100);
        }
        
        let synergyBonus = 0;
        const synergies = festival.synergies && Array.isArray(festival.synergies) ? festival.synergies : [];
        if (synergies.length > 0) {
            synergyBonus = synergies.reduce((sum, synergy) => sum + ((synergy.marketing_bonus || 0) * 100), 0);
        }
        
        return Math.min(baseEffectiveness + synergyBonus, 200);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount || 0);
    }

    formatNumber(num) {
        return new Intl.NumberFormat('en-US').format(num || 0);
    }

    showAlert(message, type = 'info') {
        // This would integrate with your existing alert system
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    initializeCharts() {
        // Initialize revenue chart
        const revenueCtx = document.getElementById('revenueChart');
        if (revenueCtx) {
            this.revenueChart = new Chart(revenueCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Revenue',
                        data: [0, 0, 0, 0],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Revenue Projection'
                        }
                    }
                }
            });
        }

        // Initialize budget chart
        const budgetCtx = document.getElementById('budgetChart');
        if (budgetCtx) {
            this.budgetChart = new Chart(budgetCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Used', 'Available'],
                    datasets: [{
                        data: [0, 100000],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Budget Usage'
                        }
                    }
                }
            });
        }

        // Initialize artist popularity chart
        const artistCtx = document.getElementById('artistPopularityChart');
        if (artistCtx) {
            this.artistPopularityChart = new Chart(artistCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Popularity',
                        data: [],
                        backgroundColor: 'rgba(255, 206, 86, 0.8)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Artist Popularity'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        // Initialize vendor quality chart
        const vendorCtx = document.getElementById('vendorQualityChart');
        if (vendorCtx) {
            this.vendorQualityChart = new Chart(vendorCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Quality',
                        data: [],
                        backgroundColor: 'rgba(153, 102, 255, 0.8)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Vendor Quality'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }

    updateCharts() {
        if (!this.festivalData) return;

        const festival = this.festivalData.festival;
        const artists = this.festivalData.artists || [];
        const vendors = this.festivalData.vendors || [];

        // Update budget chart
        if (this.budgetChart) {
            const initialBudget = 100000; // This should come from festival data
            const usedBudget = initialBudget - festival.budget;
            this.budgetChart.data.datasets[0].data = [usedBudget, festival.budget];
            this.budgetChart.update();
        }

        // Update artist popularity chart
        if (this.artistPopularityChart && artists.length > 0) {
            const names = artists.map(a => a.name);
            const popularity = artists.map(a => a.popularity);
            this.artistPopularityChart.data.labels = names;
            this.artistPopularityChart.data.datasets[0].data = popularity;
            this.artistPopularityChart.update();
        }

        // Update vendor quality chart
        if (this.vendorQualityChart && vendors.length > 0) {
            const names = vendors.map(v => v.name);
            const quality = vendors.map(v => v.quality);
            this.vendorQualityChart.data.labels = names;
            this.vendorQualityChart.data.datasets[0].data = quality;
            this.vendorQualityChart.update();
        }

        // Update revenue chart (simplified projection)
        if (this.revenueChart) {
            const baseRevenue = festival.venue_capacity * 50; // $50 per ticket
            const reputationMultiplier = festival.reputation / 100;
            const artistBonus = artists.length * 0.1;
            const projectedRevenue = baseRevenue * reputationMultiplier * (1 + artistBonus);
            
            this.revenueChart.data.datasets[0].data = [
                projectedRevenue * 0.2,
                projectedRevenue * 0.4,
                projectedRevenue * 0.7,
                projectedRevenue
            ];
            this.revenueChart.update();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
} else {
    window.DashboardManager = DashboardManager;
}

// Initialize dashboard manager - this will be called by the template
function initializeDashboard(festivalId) {
    window.dashboardManager = new DashboardManager(festivalId);
    return window.dashboardManager;
} 