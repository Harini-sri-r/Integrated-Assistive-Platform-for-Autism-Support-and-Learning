// Event delegation for delete buttons
document.addEventListener('DOMContentLoaded', () => {
    const faceGrid = document.getElementById('face-grid');
    if (faceGrid) {
        faceGrid.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const faceId = deleteBtn.getAttribute('data-delete-id');
                if (faceId) {
                    deleteFace(parseInt(faceId));
                }
            }
        });
    }
});

async function deleteFace(faceId) {
    if (!confirm('Are you sure you want to delete this face sample?')) {
        return;
    }

    try {
        const response = await fetch(`/api/face/delete/${faceId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.status === 'success') {
            // Remove the card from the UI
            const card = document.querySelector(`[data-face-id="${faceId}"]`);
            if (card) {
                card.style.transition = 'all 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';

                setTimeout(() => {
                    card.remove();

                    // Check if grid is empty
                    const grid = document.getElementById('face-grid');
                    if (grid && grid.children.length === 0) {
                        location.reload(); // Reload to show empty state
                    }
                }, 300);
            }

            // Show success message
            showNotification('Face sample deleted successfully', 'success');
        } else {
            showNotification('Error deleting face: ' + result.error, 'error');
        }
    } catch (error) {
        console.error(error);
        showNotification('Error: ' + error.message, 'error');
    }
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? 'rgba(74, 222, 128, 0.2)' : 'rgba(239, 68, 68, 0.2)'};
        border: 1px solid ${type === 'success' ? '#4ade80' : '#f87171'};
        color: ${type === 'success' ? '#4ade80' : '#f87171'};
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
