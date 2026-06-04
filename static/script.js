// =====================
// MODALS
// =====================

const loginModal = document.getElementById("login-modal");
const registerModal = document.getElementById("register-modal");
const eventModal = document.getElementById("event-modal");

const openLoginBtn = document.getElementById("open-login");
const openRegisterBtn = document.getElementById("open-register-btn");
const openRegisterLink = document.getElementById("open-register");

const closeLoginBtn = document.getElementById("close-login");
const closeRegisterBtn = document.getElementById("close-register");
const closeEventBtn = document.getElementById("close-event");

const openEventBtn = document.getElementById("open-event");

const shareModal = document.getElementById("share-modal");
const shareForm = document.getElementById("share-form");
const closeShare = document.getElementById("close-share");
const showShareFormBtn = document.getElementById("show-share-form");
const eventMenu = document.getElementById("event-menu");

if (showShareFormBtn) {

    showShareFormBtn.onclick = () => {

        eventMenu.style.display = "none";

        shareForm.style.display = "flex";

        shareForm.style.flexDirection = "column";

    };

}


function openShareModal(eventId, title) {

    shareModal.style.display = "flex";

    document.getElementById("share-title").textContent =
        title;

    shareForm.action =
        `/share_event/${eventId}`;

    document.getElementById("delete-event-btn").href =
        `/delete_event/${eventId}`;

}


// LOGIN

if (openLoginBtn) {
    openLoginBtn.onclick = () => {
        loginModal.style.display = "flex";
    };
}

if (closeLoginBtn) {
    closeLoginBtn.onclick = () => {
        loginModal.style.display = "none";
    };
}


// REGISTER

if (openRegisterBtn) {
    openRegisterBtn.onclick = () => {
        registerModal.style.display = "flex";
    };
}

if (openRegisterLink) {
    openRegisterLink.onclick = () => {
        loginModal.style.display = "none";
        registerModal.style.display = "flex";
    };
}

if (closeRegisterBtn) {
    closeRegisterBtn.onclick = () => {
        registerModal.style.display = "none";
    };
}


// EVENT

if (openEventBtn) {
    openEventBtn.onclick = () => {
        eventModal.style.display = "flex";
    };
}

if (closeEventBtn) {
    closeEventBtn.onclick = () => {
        eventModal.style.display = "none";
    };
}


// CLOSE OUTSIDE

window.onclick = (event) => {

    if (event.target === loginModal) {
        loginModal.style.display = "none";
    }

    if (event.target === registerModal) {
        registerModal.style.display = "none";
    }

    if (event.target === eventModal) {
        eventModal.style.display = "none";
    }

};



// =====================
// CALENDAR
// =====================

const calendar = document.getElementById("calendar");
const currentDateText = document.getElementById("current-date");

const months = [
    "Januar",
    "Februar",
    "Mars",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Desember"
];

const days = [
    "Man",
    "Tir",
    "Ons",
    "Tor",
    "Fre",
    "Lør",
    "Søn"
];

let currentDate = new Date();

function renderCalendar() {

    if (!calendar) return;

    calendar.innerHTML = "";

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    currentDateText.textContent =
        `${months[month]} ${year}`;

    // HEADER

    const weekLabel = document.createElement("div");
    weekLabel.classList.add("week-label");
    weekLabel.textContent = "Uke";

    calendar.appendChild(weekLabel);

    days.forEach(day => {

        const dayElement =
            document.createElement("div");

        dayElement.classList.add("day-name");
        dayElement.textContent = day;

        calendar.appendChild(dayElement);

    });

    // DATE INFO

    const firstDay =
        new Date(year, month, 1);

    let startingDay =
        firstDay.getDay();

    startingDay =
        startingDay === 0
            ? 6
            : startingDay - 1;

    const daysInMonth =
        new Date(year, month + 1, 0).getDate();

    const today =
        new Date();

    let dayCount = 1;

    let currentWeek =
        getWeekNumber(firstDay);

    // CALENDAR LOOP

    while (dayCount <= daysInMonth) {

        const weekNumber =
            document.createElement("div");

        weekNumber.classList.add("week-number");
        weekNumber.textContent = currentWeek;

        calendar.appendChild(weekNumber);

        for (let i = 0; i < 7; i++) {

            const dayBox =
                document.createElement("div");

            dayBox.classList.add("calendar-day");

            if (
                currentWeek === getWeekNumber(firstDay)
                &&
                i < startingDay
            ) {

                dayBox.classList.add("empty");

            }

            else if (dayCount > daysInMonth) {

                dayBox.classList.add("empty");

            }

            else {

                const currentDay = dayCount;

                const dayNumber =
                    document.createElement("span");

                dayNumber.classList.add("day-number");
                dayNumber.textContent = currentDay;

                dayBox.appendChild(dayNumber);

                // TODAY

                if (
                    currentDay === today.getDate()
                    &&
                    month === today.getMonth()
                    &&
                    year === today.getFullYear()
                ) {

                    dayBox.classList.add("today");

                }

                // EVENTS FROM DATABASE

                if (
                    typeof events !== "undefined"
                    &&
                    Array.isArray(events)
                ) {

                    events.forEach(eventData => {

                        const eventDate =
                            new Date(eventData.event_date);

                        if (
                            eventDate.getDate() === currentDay
                            &&
                            eventDate.getMonth() === month
                            &&
                            eventDate.getFullYear() === year
                        ) {

                            const event =
                                document.createElement("div");

                            event.classList.add("event");

                            event.textContent =
                                eventData.title;

                            event.dataset.id =
                                eventData.id;

                            event.title =
                                "Klikk for å slette";

                            event.onclick = () => {

                                openShareModal(
                                    eventData.id,
                                    eventData.title
                                );

                            };

                            dayBox.appendChild(event);

                        }

                    });

                }

                if (
                    typeof sharedEvents !== "undefined"
                    &&
                    Array.isArray(sharedEvents)
                ) {

                    sharedEvents.forEach(eventData => {

                        const eventDate =
                            new Date(eventData.event_date);

                        if (
                            eventDate.getDate() === currentDay
                            &&
                            eventDate.getMonth() === month
                            &&
                            eventDate.getFullYear() === year
                        ) {

                            const event =
                                document.createElement("div");

                            event.classList.add(
                                "event",
                                "shared-event"
                            );

                            event.textContent =
                                `${eventData.title} (${eventData.owner})`;

                            dayBox.appendChild(event);

                        }

                    });

                }

                dayCount++;

            }

            calendar.appendChild(dayBox);

        }

        currentWeek++;

    }

}

function getWeekNumber(date) {

    const tempDate =
        new Date(date);

    tempDate.setHours(0, 0, 0, 0);

    tempDate.setDate(
        tempDate.getDate() + 3 -
        (tempDate.getDay() + 6) % 7
    );

    const week1 =
        new Date(tempDate.getFullYear(), 0, 4);

    return 1 + Math.round(

        (
            (
                tempDate - week1
            ) / 86400000
            - 3
            + (
                week1.getDay() + 6
            ) % 7
        ) / 7

    );

}

renderCalendar();

const prevBtn =
    document.getElementById("prev-month");

const nextBtn =
    document.getElementById("next-month");

if (prevBtn) {

    prevBtn.onclick = () => {

        currentDate.setMonth(
            currentDate.getMonth() - 1
        );

        renderCalendar();

    };

}

if (nextBtn) {

    nextBtn.onclick = () => {

        currentDate.setMonth(
            currentDate.getMonth() + 1
        );

        renderCalendar();

    };

}