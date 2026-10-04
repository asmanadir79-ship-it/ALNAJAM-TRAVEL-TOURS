from django.urls import path
from . import views


urlpatterns = [

    # =====================================================
    # PUBLIC WEBSITE
    # =====================================================

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'contact/',
        views.contact,
        name='contact'
    ),

    path(
        'flights/',
        views.flights,
        name='flights'
    ),

    path(
        'hotels/',
        views.hotels,
        name='hotels'
    ),

    path(
        'visa/',
        views.visa,
        name='visa'
    ),

    path(
        'umrah/',
        views.umrah,
        name='umrah'
    ),

    path(
        'tours/',
        views.tours,
        name='tours'
    ),

    path(
        'about/',
        views.about,
        name='about'
    ),


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'become-agent/',
        views.become_agent,
        name='become_agent'
    ),

    path(
        "agent-dashboard/",
        views.agent_dashboard,
        name="agent_dashboard"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # =====================================================
    # FLIGHT BOOKING
    # =====================================================

    path(
        "book-flight/",
        views.book_flight,
        name="book_flight"
    ),

    path(
        'create-booking/<int:flight_id>/',
        views.create_booking,
        name='create_booking'
    ),

    path(
        'booking-success/<int:booking_id>/',
        views.booking_success,
        name='booking_success'
    ),

    path(
        'bookings/',
        views.bookings,
        name='bookings'
    ),


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'admin-dashboard/pending-agents/',
        views.pending_agents,
        name='pending_agents'
    ),

    path(
        'admin-dashboard/agents/<int:agent_id>/',
        views.admin_agent_detail,
        name='admin_agent_detail'
    ),

    path(
        'admin-dashboard/agents/<int:agent_id>/approve/',
        views.approve_agent,
        name='approve_agent'
    ),

    path(
        'admin-dashboard/agents/<int:agent_id>/reject/',
        views.reject_agent,
        name='reject_agent'
    ),

    path(
        'admin-dashboard/agents/<int:agent_id>/suspend/',
        views.suspend_agent,
        name='suspend_agent'
    ),


    # =====================================================
    # ADMIN - BOOKINGS
    # =====================================================

    path(
        'admin-dashboard/bookings/<int:booking_id>/',
        views.admin_booking_detail,
        name='admin_booking_detail'
    ),

    path(
        'admin-dashboard/bookings/<int:booking_id>/confirm/',
        views.confirm_booking,
        name='confirm_booking'
    ),

    path(
        'admin-dashboard/bookings/<int:booking_id>/cancel/',
        views.cancel_booking,
        name='cancel_booking'
    ),


    # =====================================================
    # ADMIN - GROUP TICKETS
    # =====================================================

    path(
        'admin-dashboard/group-tickets/',
        views.admin_group_tickets,
        name='admin_group_tickets'
    ),

    path(
        'admin-dashboard/group-tickets/add/',
        views.admin_add_group_ticket,
        name='admin_add_group_ticket'
    ),

    path(
        'admin-dashboard/group-tickets/<int:ticket_id>/edit/',
        views.admin_edit_group_ticket,
        name='admin_edit_group_ticket'
    ),

    path(
        'admin-dashboard/group-tickets/<int:ticket_id>/delete/',
        views.admin_delete_group_ticket,
        name='admin_delete_group_ticket'
    ),


    # =====================================================
    # AGENT - BOOKINGS
    # =====================================================

    path(
        "agent/bookings/",
        views.agent_all_bookings,
        name="agent_all_bookings"
    ),

    path(
        "agent/bookings/pending/",
        views.agent_pending_bookings,
        name="agent_pending_bookings"
    ),

    path(
        "agent/bookings/confirmed/",
        views.agent_confirmed_bookings,
        name="agent_confirmed_bookings"
    ),

    path(
        "agent/bookings/rejected/",
        views.agent_rejected_bookings,
        name="agent_rejected_bookings"
    ),

    path(
        "agent/view-ticket/<int:booking_id>/",
        views.agent_view_ticket,
        name="agent_view_ticket"
    ),


    # =====================================================
    # AGENT - OTHER BOOKING TYPES
    # =====================================================

    path(
        "agent/group-bookings/",
        views.agent_group_bookings,
        name="agent_group_bookings"
    ),

    path(
        "agent/umrah-bookings/",
        views.agent_umrah_bookings,
        name="agent_umrah_bookings"
    ),

    path(
        "agent/tour-bookings/",
        views.agent_tour_bookings,
        name="agent_tour_bookings"
    ),

    path(
        "agent/visa-bookings/",
        views.agent_visa_bookings,
        name="agent_visa_bookings"
    ),


    # =====================================================
    # AGENT - WALLET
    # =====================================================

    path(
        "agent/wallet/",
        views.agent_wallet,
        name="agent_wallet"
    ),
path(
    "agent/group-tickets/",
    views.agent_group_tickets,
    name="agent_group_tickets"
),
path(
    "agent/group-tickets/<int:group_ticket_id>/book/",
    views.create_group_booking,
    name="create_group_booking"
),

path(
    "agent/group-booking-success/<int:booking_id>/",
    views.group_booking_success,
    name="group_booking_success"
),
# =====================================================
# ADMIN - GROUP BOOKINGS
# =====================================================

path(
    'admin-dashboard/group-bookings/<int:booking_id>/',
    views.admin_group_booking_detail,
    name='admin_group_booking_detail'
),

path(
    'admin-dashboard/group-bookings/<int:booking_id>/confirm/',
    views.confirm_group_booking,
    name='confirm_group_booking'
),

path(
    'admin-dashboard/group-bookings/<int:booking_id>/reject/',
    views.reject_group_booking,
    name='reject_group_booking'
),
path(
    "agent/group-view-ticket/<int:booking_id>/",
    views.agent_group_view_ticket,
    name="agent_group_view_ticket"
),
path(
    "agency-profile/",
    views.agency_profile,
    name="agency_profile"
),
# =====================================================
# AGENT - BANKING
# =====================================================

path(
    "agent/banking/",
    views.agent_banking,
    name="agent_banking"
),

path(
    "agent/banking/",
    views.agent_banking,
    name="agency_banking"
),

path(
    "admin-dashboard/wallet-topups/<int:topup_id>/approve/",
    views.admin_approve_topup,
    name="admin_approve_topup"
),

path(
    "admin-dashboard/wallet-topups/<int:topup_id>/reject/",
    views.admin_reject_topup,
    name="admin_reject_topup"
),
path(
    "admin-dashboard/wallet-requests/",
    views.admin_wallet_requests,
    name="admin_wallet_requests"
),
path(
    "admin-dashboard/wallet-request/<int:topup_id>/",
    views.admin_wallet_request_detail,
    name="admin_wallet_request_detail"
),
path(
    "agent/wallet/export-excel/",
    views.export_wallet_excel,
    name="export_wallet_excel"
),
path(
    "agent/wallet/export-pdf/",
    views.export_wallet_pdf,
    name="export_wallet_pdf"
),
path(
    "admin-dashboard/agent-wallet/<int:agent_id>/statement/",
    views.admin_agent_wallet_statement,
    name="admin_agent_wallet_statement"
),
path(
    "admin-dashboard/agents/<int:agent_id>/wallet-statement/excel/",
    views.admin_agent_wallet_statement_excel,
    name="admin_agent_wallet_statement_excel"
),
path(
    "admin-dashboard/agent-wallet-statement/<int:agent_id>/pdf/",
    views.admin_agent_wallet_statement_pdf,
    name="admin_agent_wallet_statement_pdf"
),
 path(
        "agent/settings/",
        views.agent_settings,
        name="agent_settings"
    ),
  path(
    "admin-dashboard/umrah-packages/",
    views.admin_umrah_packages,
    name="admin_umrah_packages"
),
path(
    "admin-dashboard/umrah-packages/create/",
    views.admin_create_umrah_package,
    name="admin_create_umrah_package"
),
path(
    "admin-dashboard/umrah-packages/<int:package_id>/",
    views.admin_umrah_package_detail,
    name="admin_umrah_package_detail"
),
path(
    "admin-dashboard/umrah-packages/<int:package_id>/edit/",
    views.admin_edit_umrah_package,
    name="admin_edit_umrah_package"
),
path(
    "agent/umrah-packages/<int:package_id>/",
    views.agent_umrah_package_detail,
    name="agent_umrah_package_detail"
),
path(
    "agent/umrah-booking/create/<int:package_id>/",
    views.agent_umrah_booking_create,
    name="agent_umrah_booking_create",
),

path(
    "agent/umrah-booking/<int:package_id>/",
    views.agent_umrah_booking_create,
    name="agent_umrah_booking_create",
),

path(
    "agent/umrah-booking/success/<int:booking_id>/",
    views.agent_umrah_booking_success,
    name="agent_umrah_booking_success",
),

path(
    "agent/umrah-booking/<int:package_id>/",
    views.agent_umrah_booking_create,
    name="agent_umrah_booking_create",
),
path(
    "agent/umrah/pilgrim-details/<int:package_id>/",
    views.agent_umrah_pilgrim_details,
    name="agent_umrah_pilgrim_details",
),
# =====================================================
# ADMIN - UMRAH BOOKINGS
# =====================================================

path(
    "admin-dashboard/umrah-bookings/",
    views.admin_umrah_bookings,
    name="admin_umrah_bookings"
),

path(
    "admin-dashboard/umrah-booking/<int:booking_id>/",
    views.admin_umrah_booking_detail,
    name="admin_umrah_booking_detail"
),

path(
    "admin-dashboard/umrah-booking/<int:booking_id>/approve/",
    views.admin_approve_umrah_booking,
    name="admin_approve_umrah_booking"
),

path(
    "admin-dashboard/umrah-booking/<int:booking_id>/reject/",
    views.admin_reject_umrah_booking,
    name="admin_reject_umrah_booking"
),
path(
    "agent/umrah-ticket/<int:booking_id>/",
    views.agent_umrah_view_ticket,
    name="agent_umrah_view_ticket"
),
]