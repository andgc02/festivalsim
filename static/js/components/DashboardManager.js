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
        if (!data || !data.festival) {
            console.error('Invalid festival data received');
            return;
        }
        
        console.log('Step 1: Updating festival stats...');
        this.updateFestivalStats(data);
        
        console.log('Step 2: Updating days remaining...');
        this.updateDaysRemaining(data);
        
        console.log('Step 3: Updating lists...');
        this.updateLists(data);
        
        console.log('Step 4: Updating analytics metrics...');
        this.updateAnalyticsMetrics(data);
        
        console.log('Step 5: Updating synergies...');
        this.updateSynergies(data.synergies || []);
        this.updateVendorRelationships(data.vendor_relationships || []);
        
        console.log('=== UPDATE DASHBOARD COMPLETE ===');
    }

    updateFestivalStats(data) {
        document.getElementById('budgetDisplay').textContent = this.formatCurrency(data.festival.current_budget || data.festival.budget);
        
        const ticketsSold = data.tickets && Array.isArray(data.tickets) ? 
            data.tickets.reduce((sum, t) => sum + (t.sold_quantity || 0), 0) : 0;
        document.getElementById('ticketsSold').textContent = this.formatNumber(ticketsSold);
        
        document.getElementById('artistsCount').textContent = data.artists ? data.artists.length : 0;
        document.getElementById('vendorsCount').textContent = data.vendors ? data.vendors.length : 0;
    }

    updateDaysRemaining(data) {
        const daysUntil = data.festival.days_remaining || 365;
        document.getElementById('daysUntilFestival').textContent = daysUntil > 0 ? daysUntil : 'Today!';
    }

    updateLists(data) {
        this.updateArtistsList(data.artists || []);
        this.updateVendorsList(data.vendors || []);
        this.updateEventsList(data.events || []);
    }

    updateAnalyticsMetrics(data) {
        const tickets = data.tickets && Array.isArray(data.tickets) ? data.tickets : [];
        const totalRevenue = tickets.reduce((sum, ticket) => sum + ((ticket.sold_quantity || 0) * (ticket.price || 0)), 0);
        const budgetUsed = data.festival.budget > 0 ? 
            ((data.festival.budget - (data.festival.current_budget || data.festival.budget)) / data.festival.budget * 100).toFixed(1) : 0;
        const avgTicketPrice = tickets.length > 0 ? 
            (totalRevenue / tickets.reduce((sum, t) => sum + (t.sold_quantity || 0), 0)).toFixed(2) : 0;
        const roi = data.festival.budget > 0 ? ((totalRevenue - data.festival.budget) / data.festival.budget * 100).toFixed(1) : 0;
        
        document.getElementById('totalRevenue').textContent = this.formatCurrency(totalRevenue);
        document.getElementById('budgetUsed').textContent = budgetUsed + '%';
        document.getElementById('avgTicketPrice').textContent = this.formatCurrency(avgTicketPrice);
        document.getElementById('roi').textContent = roi + '%';
        
        // Performance Metrics
        const festivalScore = this.calculateFestivalScore(data);
        const artistSatisfaction = this.calculateArtistSatisfaction(data);
        const vendorSatisfaction = this.calculateVendorSatisfaction(data);
        const marketingEffectiveness = this.calculateMarketingEffectiveness(data);
        
        document.getElementById('festivalScore').textContent = festivalScore + '/100';
        document.getElementById('artistSatisfactionScore').textContent = artistSatisfaction;
        document.getElementById('vendorSatisfactionScore').textContent = vendorSatisfaction;
        document.getElementById('marketingEffectiveness').textContent = marketingEffectiveness + '%';
        
        // Operational Metrics
        const totalArtists = data.artists ? data.artists.length : 0;
        const totalVendors = data.vendors ? data.vendors.length : 0;
        const marketing = data.marketing && Array.isArray(data.marketing) ? data.marketing : [];
        const events = data.events && Array.isArray(data.events) ? data.events : [];
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
        
        container.innerHTML = vendors.map(vendor => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <strong>${vendor.name}</strong><br>
                    <small class="text-muted">${vendor.category} • ${vendor.type}</small>
                </div>
                <span class="badge bg-${vendor.status === 'confirmed' ? 'success' : 'warning'}">${vendor.status}</span>
            </div>
        `).join('');
    }

    updateEventsList(events) {
        const container = document.getElementById('eventsContainer');
        const unresolvedEvents = events.filter(event => !event.resolved);
        
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
        try {
            const container = document.getElementById('synergiesContainer');
            
            if (!container) {
                console.warn('Synergies container not found');
                return;
            }
            
            if (!synergies || synergies.length === 0) {
                container.innerHTML = '<p class="text-muted">No synergies available yet. Hire more artists to unlock synergies!</p>';
                return;
            }
            
            container.innerHTML = synergies.map(synergy => `
                <div class="card mb-3 border-primary">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8 col-sm-12">
                                <h6 class="card-title text-primary">
                                    <i class="fas fa-magic me-2"></i>${synergy.name || 'Synergy'}
                                </h6>
                                <p class="card-text small mb-2">${synergy.description || 'Genre synergy effect'}</p>
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <strong>Genres:</strong> ${(synergy.genres || []).join(', ')}<br>
                                        <strong>Artists:</strong> ${synergy.artist_count || 0}
                                    </small>
                                </div>
                            </div>
                            <div class="col-md-4 col-sm-12 text-end">
                                <div class="mb-2">
                                    <div class="badge bg-success mb-1">
                                        <i class="fas fa-chart-line me-1"></i>+${((synergy.marketing_bonus || 0) * 100).toFixed(0)}% Marketing
                                    </div>
                                    <div class="badge bg-info">
                                        <i class="fas fa-star me-1"></i>+${synergy.reputation_bonus || 0} Reputation
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error updating synergies:', error);
        }
    }

    updateVendorRelationships(relationships) {
        try {
            const container = document.getElementById('vendorRelationshipsContainer');
            
            if (!container) {
                console.warn('Vendor relationships container not found');
                return;
            }
            
            if (!relationships || relationships.length === 0) {
                container.innerHTML = '<p class="text-muted">No vendor relationships to display. Hire more vendors to see relationships!</p>';
                return;
            }
            
            container.innerHTML = relationships.map(relationship => {
                const isComplementary = relationship.type === 'complementary';
                const borderClass = isComplementary ? 'border-success' : 'border-warning';
                const titleClass = isComplementary ? 'text-success' : 'text-warning';
                const icon = isComplementary ? 'fa-handshake' : 'fa-exclamation-triangle';
                const bonusText = isComplementary ? 
                    `+${((relationship.bonus || 0) * 100).toFixed(0)}% Satisfaction` : 
                    `${((relationship.penalty || 0) * 100).toFixed(0)}% Satisfaction Penalty`;
                
                return `
                    <div class="card mb-3 ${borderClass}">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8 col-sm-12">
                                    <h6 class="card-title ${titleClass}">
                                        <i class="fas ${icon} me-2"></i>${relationship.vendor1 || 'Vendor 1'} & ${relationship.vendor2 || 'Vendor 2'}
                                    </h6>
                                    <p class="card-text small mb-2">${relationship.description || 'Vendor relationship effect'}</p>
                                    <div class="badge ${isComplementary ? 'bg-success' : 'bg-warning'}">
                                        ${bonusText}
                                    </div>
                                </div>
                                <div class="col-md-4 col-sm-12 text-end">
                                    <div class="mb-2">
                                        <small class="text-muted">
                                            <strong>Type:</strong> ${(relationship.type || 'unknown').charAt(0).toUpperCase() + (relationship.type || 'unknown').slice(1)}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Error updating vendor relationships:', error);
        }
    }

    calculateFestivalScore(data) {
        let score = 0;
        
        const currentBudget = data.festival.current_budget || data.festival.budget;
        const budgetEfficiency = data.festival.budget > 0 ? (currentBudget / data.festival.budget) * 100 : 0;
        score += Math.min(budgetEfficiency, 25);
        
        const artists = data.artists && Array.isArray(data.artists) ? data.artists : [];
        if (artists.length > 0) {
            const avgArtistPopularity = artists.reduce((sum, artist) => sum + (artist.popularity || 0), 0) / artists.length;
            score += (avgArtistPopularity / 100) * 25;
        }
        
        const vendors = data.vendors && Array.isArray(data.vendors) ? data.vendors : [];
        const vendorCategories = new Set(vendors.map(v => v.category || v.type || 'unknown'));
        score += Math.min(vendorCategories.size * 5, 20);
        
        const marketing = data.marketing && Array.isArray(data.marketing) ? data.marketing : [];
        const activeMarketing = marketing.filter(m => m.status === 'active');
        score += Math.min(activeMarketing.length * 5, 15);
        
        const tickets = data.tickets && Array.isArray(data.tickets) ? data.tickets : [];
        const totalTickets = tickets.reduce((sum, t) => sum + (t.sold_quantity || 0), 0);
        score += Math.min(totalTickets / 10, 15);
        
        return Math.round(score);
    }

    calculateArtistSatisfaction(data) {
        const artists = data.artists && Array.isArray(data.artists) ? data.artists : [];
        if (artists.length === 0) return 'N/A';
        
        const confirmedArtists = artists.filter(a => a.status === 'confirmed');
        const satisfactionRate = (confirmedArtists.length / artists.length) * 100;
        
        if (satisfactionRate >= 90) return 'Excellent';
        if (satisfactionRate >= 75) return 'Good';
        if (satisfactionRate >= 50) return 'Fair';
        return 'Poor';
    }

    calculateVendorSatisfaction(data) {
        const vendors = data.vendors && Array.isArray(data.vendors) ? data.vendors : [];
        if (vendors.length === 0) return 'N/A';
        
        const confirmedVendors = vendors.filter(v => v.status === 'confirmed');
        const satisfactionRate = (confirmedVendors.length / vendors.length) * 100;
        
        if (satisfactionRate >= 90) return 'Excellent';
        if (satisfactionRate >= 75) return 'Good';
        if (satisfactionRate >= 50) return 'Fair';
        return 'Poor';
    }

    calculateMarketingEffectiveness(data) {
        const marketing = data.marketing && Array.isArray(data.marketing) ? data.marketing : [];
        const activeMarketing = marketing.filter(m => m.status === 'active');
        let baseEffectiveness = 100;
        
        if (activeMarketing.length > 0) {
            const totalEffectiveness = activeMarketing.reduce((sum, campaign) => sum + (campaign.effectiveness || 0), 0);
            baseEffectiveness = Math.min(Math.round(totalEffectiveness * 100), 100);
        }
        
        let synergyBonus = 0;
        const synergies = data.synergies && Array.isArray(data.synergies) ? data.synergies : [];
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