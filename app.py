import streamlit as st
import pandas as pd
from datetime import date
from streamlit_calendar import calendar  # <--- Componente de calendario

from src.database import DatabaseManager
from src.repositories import (
    ClientRepository, PetRepository, AppointmentRepository, 
    MedicalRecordRepository, BillingRepository, ReviewRepository, UserRepository
)
from src.services import ClinicService, AuthService
from src.seeder import DataSeeder  # <--- Importamos el Seeder
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review

# --- Configuración de la Página (Debe ser la primera llamada) ---
st.set_page_config(page_title="VetManager Pro", layout="wide", page_icon="🐾")

# --- Inyección de Dependencias (Composition Root) ---
db = DatabaseManager()
db.initialize_db()

# Inicialización de Repositorios
client_repo = ClientRepository(db)
pet_repo = PetRepository(db)
appt_repo = AppointmentRepository(db)
mr_repo = MedicalRecordRepository(db)
bill_repo = BillingRepository(db)
review_repo = ReviewRepository(db)
user_repo = UserRepository(db)

# Inicialización de Servicios
service = ClinicService(client_repo, pet_repo, appt_repo, mr_repo, bill_repo, review_repo)
auth_service = AuthService(user_repo)

# --- Carga de Datos Iniciales (Seeding) ---
# Usamos el Seeder dedicado en lugar del servicio para cumplir SOLID (SRP)
seeder = DataSeeder(client_repo, pet_repo, appt_repo, mr_repo, bill_repo, review_repo)
seeder.seed()

# Asegurar admin
auth_service.create_admin_if_not_exists()

# --- Gestión de Sesión y Login ---

def login_page():
    """Vista de inicio de sesión."""
    st.title("🔐 Iniciar Sesión - VetManager")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### Credenciales")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                user = auth_service.login(username, password)
                if user:
                    st.session_state['user'] = user
                    st.success(f"Bienvenido {user.username}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

def logout():
    """Cierra la sesión del usuario."""
    if 'user' in st.session_state:
        del st.session_state['user']
    st.rerun()

# --- Aplicación Principal ---

def main_app():
    """Contiene la lógica principal de la aplicación una vez logueado."""
    st.sidebar.title("🐾 VetManager")
    
    # Info de usuario y Logout
    if 'user' in st.session_state:
        st.sidebar.markdown(f"👤 **{st.session_state['user'].username}**")
        if st.sidebar.button("Cerrar Sesión"):
            logout()
    
    st.sidebar.divider()
    
    # Menú de Navegación
    menu = st.sidebar.radio(
        "Navegación", 
        ["Inicio", "Clientes", "Mascotas", "Calendario & Citas", "Facturación", "Reseñas"]
    )

    if menu == "Inicio":
        show_home()
    elif menu == "Clientes":
        show_clients()
    elif menu == "Mascotas":
        show_pets()
    elif menu == "Calendario & Citas":
        show_calendar()
    elif menu == "Facturación":
        show_billing()
    elif menu == "Reseñas":
        show_reviews()

def show_home():
    st.title("Bienvenido a VetManager Pro")
    st.markdown("### Sistema de Gestión Veterinaria Integral")
    
    col1, col2, col3 = st.columns(3)
    clients = service.list_clients()
    pets = service.list_pets()
    appts = service.list_appointments()
    
    with col1:
        st.metric("Clientes Registrados", len(clients))
    with col2:
        st.metric("Mascotas Activas", len(pets))
    with col3:
        st.metric("Citas Programadas", len(appts))

    st.image("https://images.unsplash.com/photo-1553688738-a278b9f063e0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", caption="Cuidado profesional para tus mascotas")

def show_clients():
    st.header("Gestión de Clientes")
    
    clients = service.list_clients()
    client_data = [vars(c) for c in clients] if clients else []
    client_df = pd.DataFrame(client_data)
    
    col_register, col_actions = st.columns([1, 1])

    with col_register:
        with st.expander("➕ Registrar Nuevo Cliente"):
            with st.form("new_client_form"):
                name = st.text_input("Nombre Completo")
                email = st.text_input("Email")
                phone = st.text_input("Teléfono")
                submitted = st.form_submit_button("Guardar")
                if submitted:
                    try:
                        service.add_client(name, email, phone)
                        st.success("Cliente guardado correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        st.subheader("Listado de Clientes")
        if not clients:
            st.info("No hay clientes registrados.")
        else:
            st.dataframe(client_df, use_container_width=True)

    with col_actions:
        st.subheader("Acciones")
        if clients:
            client_options = {c.name: c for c in clients}
            
            # Eliminar
            st.markdown("##### Eliminar Cliente")
            client_to_delete_name = st.selectbox("Seleccionar Cliente para eliminar", 
                                                 list(client_options.keys()), 
                                                 key="delete_client_select")
            client_to_delete = client_options[client_to_delete_name]

            if st.button("🔴 Eliminar Cliente", key="delete_client_btn"):
                service.delete_client(client_to_delete.id)
                st.warning(f"Cliente {client_to_delete.name} eliminado.")
                st.rerun()
                
            st.divider()

            # Editar
            st.markdown("##### Editar Cliente")
            client_to_edit_name = st.selectbox("Seleccionar Cliente para editar", 
                                               list(client_options.keys()),
                                               key="edit_client_select")
            client_to_edit = client_options[client_to_edit_name]
            
            with st.form("edit_client_form"):
                st.markdown(f"**Editando ID:** {client_to_edit.id}")
                edit_name = st.text_input("Nombre Completo", value=client_to_edit.name)
                edit_email = st.text_input("Email", value=client_to_edit.email)
                edit_phone = st.text_input("Teléfono", value=client_to_edit.phone)
                
                edit_submitted = st.form_submit_button("Actualizar Cliente")
                
                if edit_submitted:
                    try:
                        updated_client = Client(client_to_edit.id, edit_name, edit_email, edit_phone)
                        service.update_client(updated_client)
                        st.success(f"Cliente {edit_name} actualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No hay clientes para realizar acciones.")

def show_pets():
    st.header("Gestión de Mascotas")
    
    clients = service.list_clients()
    client_options = {c.name: c.id for c in clients}
    client_id_to_name = {c.id: c.name for c in clients}
    pets = service.list_pets()
    
    col_register, col_actions = st.columns([1, 1])
    
    with col_register:
        with st.expander("➕ Registrar Nueva Mascota"):
            if not clients:
                st.warning("Debes registrar un cliente primero.")
            else:
                with st.form("new_pet"):
                    name = st.text_input("Nombre Mascota")
                    species = st.selectbox("Especie", ["Perro", "Gato", "Ave", "Roedor", "Otro"])
                    breed = st.text_input("Raza")
                    age = st.number_input("Edad", min_value=0, step=1)
                    owner_name = st.selectbox("Dueño", list(client_options.keys()))
                    
                    submitted = st.form_submit_button("Guardar Mascota")
                    if submitted:
                        try:
                            service.add_pet(name, species, breed, age, client_options[owner_name])
                            st.success("Mascota añadida")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        st.subheader("Historial Médico")
        if not pets:
            st.info("No hay mascotas registradas.")
        else:
            pet_history_options = {f"{p.name} (ID: {p.id})": p for p in pets}
            pet_to_view_key = st.selectbox("Seleccionar Mascota para ver Historial", 
                                           list(pet_history_options.keys()), 
                                           key="view_history_select_key")
            pet_to_view = pet_history_options[pet_to_view_key]
            
            history = service.get_medical_history_by_pet(pet_to_view.id)
            
            if history:
                df_history = pd.DataFrame(history, columns=["ID Reg.", "Fecha Cita", "Motivo", "Diagnóstico", "Tratamiento", "Notas"])
                st.dataframe(df_history, use_container_width=True)
            else:
                st.info(f"'{pet_to_view.name}' no tiene historial médico registrado.")

    with col_actions:
        st.subheader("Listado y Acciones")
        
        if pets:
            pet_data = [vars(p) for p in pets]
            pet_df = pd.DataFrame(pet_data)
            pet_df['Dueño'] = pet_df['client_id'].map(client_id_to_name)
            st.dataframe(pet_df.drop(columns=['client_id']), use_container_width=True)
            
            st.divider()
            st.markdown("##### 📝 Añadir Registro Médico")
            
            all_appts = service.list_appointments()
            target_pet_id = pet_to_view.id if 'pet_to_view' in locals() else pets[0].id
            available_appts = [a for a in all_appts if a.pet_id == target_pet_id]

            if available_appts:
                appt_options = {f"ID {a.id} - {a.date} ({a.reason})": a.id for a in available_appts}
                with st.form("new_medical_record_form"):
                    selected_appt_key = st.selectbox("Asociar a Cita", 
                                                     list(appt_options.keys()), 
                                                     key="record_appt_select")
                    appt_id = appt_options[selected_appt_key]
                    diagnosis = st.text_area("Diagnóstico Principal", height=100)
                    treatment = st.text_area("Tratamiento / Medicación", height=100)
                    notes = st.text_area("Notas Adicionales", height=50)
                    
                    if st.form_submit_button("Guardar Registro"):
                        try:
                            service.add_medical_record(appt_id, diagnosis, treatment, notes)
                            st.success(f"Registro añadido.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                st.info(f"No hay citas disponibles para esta mascota.")
        else:
             st.info("No hay mascotas.")

        # Editar Mascota (Omitido por brevedad, similar a clientes)

def show_calendar():
    st.header("📅 Calendario de Citas")
    
    pets = service.list_pets()
    pet_options = {f"{p.name} ({p.species})": p.id for p in pets}
    appts = service.list_appointments()
    
    # --- CALENDARIO VISUAL ---
    calendar_events = []
    for a in appts:
        pet_name = next((p.name for p in pets if p.id == a.pet_id), "Desconocido")
        # Color coding
        color = "#28a745" if a.status == "Completada" else "#dc3545" # Verde o Rojo
        if a.status == "Pendiente": color = "#ffc107" # Amarillo

        calendar_events.append({
            "title": f"{pet_name} - {a.reason}",
            "start": str(a.date),
            "end": str(a.date),
            "backgroundColor": color,
            "borderColor": color,
            "allDay": True
        })

    calendar_options = {
        "editable": True,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek",
        },
        "initialView": "dayGridMonth",
    }
    
    if calendar_events:
        st.markdown("### Vista Mensual")
        calendar(events=calendar_events, options=calendar_options)
        st.divider()

    # --- AGENDAR Y LISTAR ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Agendar Cita")
        if not pets:
            st.warning("Registra una mascota primero.")
        else:
            with st.form("appt_form"):
                pet_name = st.selectbox("Mascota", list(pet_options.keys()), key="appt_pet_select")
                date_val = st.date_input("Fecha")
                reason = st.text_area("Motivo")
                submit = st.form_submit_button("Agendar")
                
                if submit:
                    try:
                        service.book_appointment(pet_options[pet_name], date_val, reason)
                        st.success("Cita agendada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        st.subheader("Listado de Citas")
        if appts:
            data = []
            for a in appts:
                p_name = next((p.name for p in pets if p.id == a.pet_id), "Desconocido")
                data.append({"ID": a.id, "Fecha": a.date, "Mascota": p_name, "Motivo": a.reason, "Estado": a.status})
            
            df = pd.DataFrame(data)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            st.dataframe(df, use_container_width=True)
            
            # Eliminar Cita
            st.markdown("##### Cancelar Cita")
            appt_id_to_delete = st.selectbox("Seleccionar ID", [a.id for a in appts], key="del_appt")
            if st.button("🔴 Eliminar", key="del_btn"):
                service.delete_appointment(appt_id_to_delete)
                st.rerun()
        else:
            st.info("No hay citas programadas")

def show_billing():
    st.header("💰 Gestión de Facturación")
    
    clients = service.list_clients()
    client_options = {f"{c.name} (ID: {c.id})": c.id for c in clients}
    client_id_to_name = {c.id: c.name for c in clients}
    
    col_generate, col_list = st.columns([1, 2])
    
    with col_generate:
        st.subheader("Nueva Factura")
        if clients:
            with st.form("new_invoice_form"):
                client_name_key = st.selectbox("Cliente", list(client_options.keys()), key="invoice_client_select")
                invoice_date = st.date_input("Fecha", value=date.today())
                total_amount = st.number_input("Total (€)", min_value=0.01, step=5.00)
                
                if st.form_submit_button("Emitir Factura"):
                    try:
                        service.generate_invoice(client_options[client_name_key], total_amount, invoice_date) 
                        st.success("Factura generada.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No hay clientes.")

    with col_list:
        st.subheader("Historial de Facturas")
        invoices = service.list_invoices()
        if invoices:
            data = [vars(i) for i in invoices]
            df = pd.DataFrame(data)
            df['Cliente'] = df['client_id'].map(client_id_to_name)
            df = df.drop(columns=['client_id']).rename(columns={'total_amount': 'Monto (€)'})
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay facturas.")

def show_reviews():
    st.header("⭐ Reseñas")
    
    clients = service.list_clients()
    client_options = {f"{c.name} (ID: {c.id})": c.id for c in clients}
    
    col_submit, col_list = st.columns([1, 2])
    
    with col_submit:
        st.subheader("Nueva Reseña")
        if clients:
            with st.form("new_review_form"):
                client_name_key = st.selectbox("Cliente", list(client_options.keys()), key="review_client_select")
                rating = st.slider("Nota", 1, 5, 5)
                comment = st.text_area("Comentario")
                
                if st.form_submit_button("Enviar"):
                    service.add_review(client_options[client_name_key], rating, comment) 
                    st.success("Reseña enviada.")
                    st.rerun()
        else:
            st.warning("No hay clientes.")
                        
    with col_list:
        st.subheader("Feedback Recibido")
        reviews = service.list_reviews()
        if reviews:
            client_id_to_name = {c.id: c.name for c in clients}
            data = [vars(r) for r in reviews]
            df = pd.DataFrame(data)
            df['Cliente'] = df['client_id'].map(client_id_to_name)
            df['Calificación'] = df['rating'].apply(lambda x: "⭐" * x)
            st.dataframe(df[['Cliente', 'Calificación', 'comment', 'date']], use_container_width=True)
        else:
            st.info("No hay reseñas.")

# --- ENTRY POINT ---
def main():
    if 'user' not in st.session_state:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()