# Festival Simulator - Refactoring Guide

## Overview

This guide explains the refactored structure that makes the Festival Simulator more modular and maintainable.

## Directory Structure

```
festivalsim/
├── templates/
│   ├── components/           # Reusable HTML components
│   │   ├── stats_card.html
│   │   ├── analytics_card.html
│   │   ├── sidebar_card.html
│   │   └── dashboard_modals.html
│   ├── dashboard.html        # Original dashboard (bloated)
│   └── dashboard_refactored.html  # New modular dashboard
├── static/
│   └── js/
│       └── components/       # JavaScript modules
│           └── DashboardManager.js
└── app.py                   # Main Flask application
```

## Component System

### 1. HTML Components (Jinja2 Macros)

#### Stats Card Component
```html
<!-- templates/components/stats_card.html -->
{% macro stats_card(id, value, label, icon="", color="primary") %}
<div class="col-md-2">
    <div class="stats-card">
        <div class="stats-number" id="{{ id }}">{{ value }}</div>
        <div class="stats-label">
            {% if icon %}<i class="fas {{ icon }} me-1"></i>{% endif %}{{ label }}
        </div>
    </div>
</div>
{% endmacro %}
```

**Usage:**
```html
{% from "components/stats_card.html" import stats_card %}
{{ stats_card('budgetDisplay', "$100,000", 'Current Budget', 'fa-dollar-sign') }}
```

#### Analytics Card Component
```html
<!-- templates/components/analytics_card.html -->
{% macro analytics_card(title, icon, color="info") %}
<div class="col-md-6 mb-4">
    <h6 class="text-{{ color }} mb-3">
        <i class="fas {{ icon }} me-2"></i>{{ title }}
    </h6>
    <div class="row">
        {{ caller() }}
    </div>
</div>
{% endmacro %}
```

**Usage:**
```html
{% call analytics_card('Financial Metrics', 'fa-dollar-sign', 'primary') %}
    {{ metric_item('totalRevenue', 'Total Revenue', '0', '$') }}
    {{ metric_item('budgetUsed', 'Budget Used', '0', '', '%') }}
{% endcall %}
```

### 2. JavaScript Modules

#### DashboardManager Class
The `DashboardManager` class encapsulates all dashboard functionality:

```javascript
// static/js/components/DashboardManager.js
class DashboardManager {
    constructor(festivalId) {
        this.festivalId = festivalId;
        this.festivalData = null;
        this.lastDataUpdate = 0;
        this.CACHE_DURATION = 5000;
    }

    async loadFestivalData(forceRefresh = false) { /* ... */ }
    updateDashboard(data) { /* ... */ }
    updateFestivalStats(data) { /* ... */ }
    // ... other methods
}
```

**Usage:**
```javascript
const dashboardManager = new DashboardManager(festivalId);
await dashboardManager.loadFestivalData();
```

## Benefits of Refactoring

### 1. **Reusability**
- Components can be used across multiple pages
- Consistent styling and behavior
- Easy to maintain and update

### 2. **Maintainability**
- Smaller, focused files
- Clear separation of concerns
- Easier to debug and test

### 3. **Performance**
- JavaScript modules can be loaded asynchronously
- Better caching strategies
- Reduced code duplication

### 4. **Scalability**
- Easy to add new components
- Modular architecture supports growth
- Clear patterns for new developers

## Migration Guide

### From Original to Refactored

1. **Replace the dashboard template:**
   ```python
   # In app.py, change the route to use the refactored template
   @app.route('/dashboard/<int:festival_id>')
   def dashboard(festival_id):
       festival = Festival.query.get_or_404(festival_id)
       festivals = Festival.query.all()
       
       # Use the refactored template
       return render_template('dashboard_refactored.html', festival=festival, festivals=festivals)
   ```

2. **Update JavaScript initialization:**
   ```javascript
   // Old way (inline functions)
   function updateDashboard(data) { /* ... */ }
   
   // New way (modular)
   const dashboardManager = new DashboardManager(festivalId);
   await dashboardManager.loadFestivalData();
   ```

3. **Use components in new templates:**
   ```html
   {% from "components/stats_card.html" import stats_card %}
   {% from "components/analytics_card.html" import analytics_card, metric_item %}
   
   {{ stats_card('budgetDisplay', budget, 'Current Budget', 'fa-dollar-sign') }}
   ```

## Creating New Components

### 1. HTML Component
```html
<!-- templates/components/my_component.html -->
{% macro my_component(param1, param2, optional_param="default") %}
<div class="my-component">
    <h3>{{ param1 }}</h3>
    <p>{{ param2 }}</p>
    {% if optional_param %}
        <span class="badge">{{ optional_param }}</span>
    {% endif %}
</div>
{% endmacro %}
```

### 2. JavaScript Module
```javascript
// static/js/components/MyComponent.js
class MyComponent {
    constructor(config) {
        this.config = config;
        this.init();
    }

    init() {
        // Initialize component
    }

    update(data) {
        // Update component with new data
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MyComponent;
} else {
    window.MyComponent = MyComponent;
}
```

## Best Practices

### 1. **Component Design**
- Keep components focused and single-purpose
- Use clear, descriptive names
- Provide sensible defaults for optional parameters

### 2. **JavaScript Modules**
- Use ES6 classes for organization
- Implement proper error handling
- Provide clear interfaces for other modules

### 3. **Template Organization**
- Group related components in subdirectories
- Use consistent naming conventions
- Document component usage with examples

### 4. **Performance**
- Lazy load components when possible
- Implement proper caching strategies
- Minimize DOM queries and updates

## Future Enhancements

### 1. **Component Library**
- Create a comprehensive component library
- Add component documentation and examples
- Implement component testing

### 2. **Build System**
- Add a build process for JavaScript modules
- Implement CSS preprocessing
- Add asset optimization

### 3. **Advanced Features**
- Add component state management
- Implement component lifecycle hooks
- Add component composition patterns

## Conclusion

The refactored structure provides a solid foundation for scaling the Festival Simulator. The modular approach makes the codebase more maintainable, reusable, and easier to extend with new features.

By following the patterns established in this guide, you can continue to build upon this architecture and create a robust, scalable application. 