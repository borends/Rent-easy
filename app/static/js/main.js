// Инициализация Socket.IO для чата
if (document.querySelector('.chat-container')) {
    const socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to Socket.IO');
    });
    
    socket.on('new_message', (data) => {
        const chatContainer = document.querySelector('.chat-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.sender_id === currentUserId ? 'message-sent' : 'message-received'}`;
        messageDiv.textContent = data.body;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    });
    
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const messageInput = document.getElementById('message-input');
            const recipientId = messageForm.dataset.recipientId;
            
            socket.emit('send_message', {
                recipient_id: recipientId,
                message: messageInput.value
            });
            
            messageInput.value = '';
        });
    }
}

// Предварительный просмотр изображений при загрузке
function previewImages(input) {
    const preview = document.getElementById('image-preview');
    preview.innerHTML = '';
    
    if (input.files) {
        Array.from(input.files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'img-thumbnail m-1';
                img.style.maxHeight = '150px';
                preview.appendChild(img);
            }
            reader.readAsDataURL(file);
        });
    }
}

// Фильтрация объявлений
const filterForm = document.getElementById('filter-form');
if (filterForm) {
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);
        window.location.href = `/properties/search?${params.toString()}`;
    });
}