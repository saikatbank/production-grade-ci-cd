const API_BASE = '/api/v1';

const form = document.getElementById('add-item-form');
const list = document.getElementById('item-list');

// Fetch and display items
async function fetchItems() {
    try {
        const response = await fetch(`${API_BASE}/items/`);
        const items = await response.json();

        list.innerHTML = ''; // Clear loading
        if(items.length === 0) {
            list.innerHTML = '<p style="color: var(--text-muted)">No items found. Create one above!</p>';
            return;
        }

        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'item-card';
            el.innerHTML = `
                <div class="item-content">
                    <h3>${item.title}</h3>
                    <p>${item.description || "No description provided."}</p>
                </div>
                <span class="badge ${item.is_active ? '' : 'inactive'}">${item.is_active ? 'Active' : 'Inactive'}</span>
            `;
            list.appendChild(el);
        });
    } catch(err) {
        list.innerHTML = '<p style="color: #dc2626;">Error loading items.</p>';
        console.error(err);
    }
}

// Handle form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('title').value;
    const desc = document.getElementById('description').value;
    const isActive = document.getElementById('is_active').checked;

    const submitBtn = form.querySelector('button');
    submitBtn.textContent = 'Adding...';
    submitBtn.disabled = true;

    try {
        await fetch(`${API_BASE}/items/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                description: desc,
                is_active: isActive
            })
        });

        // Reset and reload
        form.reset();
        await fetchItems();
    } catch(err) {
        alert("Failed to add item");
        console.error(err);
    } finally {
        submitBtn.textContent = 'Add Item';
        submitBtn.disabled = false;
    }
});

// Init
fetchItems();
