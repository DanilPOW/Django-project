document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.querySelector('.image-gallery');
    const modal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const closeButton = document.querySelector('.close-button');

    if (gallery) {
        const scrollStep = 150;
        let lastScrollTime = 0;
        const scrollDelay = 100;

        const scrollGallery = (direction) => {
            const currentTime = Date.now();
            if (currentTime - lastScrollTime < scrollDelay) return;
            lastScrollTime = currentTime;

            const currentScroll = gallery.scrollLeft;
            const maxScroll = gallery.scrollWidth - gallery.clientWidth;

            if (direction === 'left') {
                gallery.scrollTo({
                    left: Math.max(currentScroll - scrollStep, 0),
                    behavior: 'smooth',
                });
            } else if (direction === 'right') {
                gallery.scrollTo({
                    left: Math.min(currentScroll + scrollStep, maxScroll),
                    behavior: 'smooth',
                });
            }
        };

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                scrollGallery('left');
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                scrollGallery('right');
            }
        });

        gallery.addEventListener('click', (e) => {
            if (e.target.tagName === 'IMG') {
                modalImage.src = e.target.src;
                modal.classList.remove('hidden');
            }
        });

        closeButton.addEventListener('click', () => {
            modal.classList.add('hidden');
            modalImage.src = '';
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                modalImage.src = '';
            }
        });
    }
});
