import streamlit as st
import pandas as pd
from src.database import DatabaseManager
from src.repositories import ClientRepository, PetRepository, AppointmentRepository, MedicalRecordRepository, BillingRepository, ReviewRepository # <--- AÑADIDO ReviewRepository
from src.services import ClinicService
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review # <--- AÑADIDO Review
from datetime import date

# --- Inyección de Dependencias (Composition Root) ---
db = DatabaseManager()
db.initialize_db()

client_repo = ClientRepository(db)
pet_repo = PetRepository(db)
appt_repo = AppointmentRepository(db)
mr_repo = MedicalRecordRepository(db)
bill_repo = BillingRepository(db)
review_repo = ReviewRepository(db) # <--- INICIALIZACIÓN AÑADIDA

# Asegurarse de que todos los 6 repositorios se pasen al servicio:
service = ClinicService(client_repo, pet_repo, appt_repo, mr_repo, bill_repo, review_repo)

# Carga datos de prueba si está vacío
service.seed_data()

# --- Configuración de la Página ---
st.set_page_config(page_title="VetManager Pro", layout="wide", page_icon="🐾")

# --- UI Styling & Estructura ---
def main():
    st.sidebar.title("🐾 VetManager")
    menu = st.sidebar.radio("Navegación", ["Inicio", "Clientes", "Mascotas", "Calendario & Citas", "Facturación", "Reseñas"]) # <--- AÑADIDO Reseñas

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
    elif menu == "Reseñas": # <--- NUEVA OPCIÓN
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
    
    # Listado de clientes
    clients = service.list_clients()
    client_df = pd.DataFrame([vars(c) for c in clients])
    
    col_register, col_actions = st.columns([1, 1])

    with col_register:
        # --- SECCIÓN REGISTRO ---
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
        
        # --- LISTADO DE CLIENTES ---
        st.subheader("Listado de Clientes")
        if not clients:
            st.info("No hay clientes registrados.")
        else:
            st.dataframe(client_df, use_container_width=True)


    with col_actions:
        st.subheader("Acciones")
        if clients:
            client_options = {c.name: c for c in clients}
            
            # --- SECCIÓN ELIMINAR CLIENTE ---
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

            # --- SECCIÓN EDITAR CLIENTE ---
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
                        success = service.update_client(updated_client)
                        if success:
                            st.success(f"Cliente {edit_name} actualizado correctamente.")
                            st.rerun()
                        else:
                            st.error("Error al actualizar (cliente no encontrado).")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No hay clientes para realizar acciones.")


def show_pets():
    st.header("Gestión de Mascotas")
    
    # Variables de inicio
    clients = service.list_clients()
    client_options = {c.name: c.id for c in clients}
    client_id_to_name = {c.id: c.name for c in clients}
    pets = service.list_pets()
    
    col_register, col_actions = st.columns([1, 1])
    
    with col_register:
        # --- REGISTRO DE NUEVA MASCOTA ---
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

        # --- VISUALIZACIÓN DE HISTORIAL MÉDICO ---
        st.subheader("Historial Médico")
        if not pets:
            st.info("No hay mascotas registradas.")
        else:
            pet_history_options = {f"{p.name} (ID: {p.id})": p for p in pets}
            
            # CLAVE ÚNICA APLICADA: view_history_select_key
            pet_to_view_key = st.selectbox("Seleccionar Mascota para ver Historial", 
                                           list(pet_history_options.keys()), 
                                           key="view_history_select_key")
            pet_to_view = pet_history_options[pet_to_view_key]
            
            # Obtener el historial
            history = service.get_medical_history_by_pet(pet_to_view.id)
            
            if history:
                df_history = pd.DataFrame(history, columns=["ID Reg.", "Fecha Cita", "Motivo", "Diagnóstico", "Tratamiento", "Notas"])
                st.dataframe(df_history, use_container_width=True)
            else:
                st.info(f"'{pet_to_view.name}' no tiene historial médico registrado.")

    # Columna de Acciones (Listado y Edición)
    with col_actions:
        st.subheader("Listado y Acciones")
        
        if not pets:
            st.info("No hay mascotas registradas.")
            return 
        
        # Listado
        pet_df = pd.DataFrame([vars(p) for p in pets])
        pet_df['Dueño'] = pet_df['client_id'].map(client_id_to_name)
        st.dataframe(pet_df.drop(columns=['client_id']), use_container_width=True)
        
        # --- SECCIÓN AÑADIR REGISTRO MÉDICO ---
        st.divider()
        st.markdown("##### 📝 Añadir Registro Médico a una Cita")
        
        all_appts = service.list_appointments()
        
        # Filtramos citas que pertenezcan a la mascota seleccionada para el historial
        available_appts = [
            a for a in all_appts 
            if a.pet_id == pet_to_view.id
        ]

        if available_appts:
            # Opciones de citas para el selectbox
            appt_options = {
                f"ID {a.id} - {a.date} ({a.reason})": a.id 
                for a in available_appts
            }
            
            with st.form("new_medical_record_form"):
                selected_appt_key = st.selectbox("Asociar a Cita", 
                                                 list(appt_options.keys()), 
                                                 key="record_appt_select")
                appt_id = appt_options[selected_appt_key]
                
                diagnosis = st.text_area("Diagnóstico Principal", height=100)
                treatment = st.text_area("Tratamiento / Medicación", height=100)
                notes = st.text_area("Notas Adicionales (Opcional)", height=50)
                
                record_submitted = st.form_submit_button("Guardar Registro")
                
                if record_submitted:
                    try:
                        if not diagnosis or not treatment:
                            st.error("Diagnóstico y Tratamiento son campos obligatorios.")
                        else:
                            service.add_medical_record(appt_id, diagnosis, treatment, notes)
                            st.success(f"Registro médico añadido a Cita ID {appt_id}.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar registro: {e}")
        else:
            st.info(f"No hay citas para {pet_to_view.name} a las que se pueda añadir un registro.")
        
        # --- SECCIÓN EDITAR MASCOTA ---
        st.divider()
        st.markdown("##### Editar Mascota")
        
        valid_pets = [p for p in pets if p.client_id in client_id_to_name]
        
        if not valid_pets:
            st.warning("No hay mascotas con dueños válidos para editar.")
        else:
            pet_options = {f"{p.name} (ID: {p.id})": p for p in valid_pets}
            
            # CLAVE ÚNICA APLICADA: edit_pet_select_key
            pet_to_edit_key = st.selectbox("Seleccionar Mascota para editar", 
                                           list(pet_options.keys()), 
                                           key="edit_pet_select_key") 
            pet_to_edit = pet_options[pet_to_edit_key]
            
            current_owner_name = client_id_to_name.get(pet_to_edit.client_id)
            
            owner_names_list = list(client_options.keys())
            if current_owner_name in owner_names_list:
                current_owner_index = owner_names_list.index(current_owner_name)
            else:
                current_owner_index = 0
            
            with st.form("edit_pet_form"):
                st.markdown(f"**Editando ID:** {pet_to_edit.id}")
                edit_name = st.text_input("Nombre Mascota", value=pet_to_edit.name)
                
                species_list = ["Perro", "Gato", "Ave", "Roedor", "Otro"]
                current_species_index = species_list.index(pet_to_edit.species)
                # CLAVE ÚNICA APLICADA: edit_species_select
                edit_species = st.selectbox("Especie", species_list, index=current_species_index, key="edit_species_select")
                
                edit_breed = st.text_input("Raza", value=pet_to_edit.breed)
                edit_age = st.number_input("Edad", min_value=0, value=pet_to_edit.age, step=1)
                
                # CLAVE ÚNICA APLICADA: edit_owner_select
                edit_owner_name = st.selectbox("Dueño", owner_names_list, index=current_owner_index, key="edit_owner_select")
                edit_client_id = client_options[edit_owner_name]

                edit_submitted = st.form_submit_button("Actualizar Mascota")
                
                if edit_submitted:
                    try:
                        updated_pet = Pet(pet_to_edit.id, edit_name, edit_species, edit_breed, edit_age, edit_client_id)
                        success = service.update_pet(updated_pet)
                        if success:
                            st.success(f"Mascota {edit_name} actualizada correctamente.")
                            st.rerun()
                        else:
                            st.error("Error al actualizar (mascota no encontrada).")
                    except Exception as e:
                        st.error(f"Error: {e}")

def show_calendar():
    st.header("📅 Calendario de Citas")
    
    pets = service.list_pets()
    pet_options = {f"{p.name} ({p.species})": p.id for p in pets}
    appts = service.list_appointments()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Agendar Cita")
        if not pets:
            st.warning("Debes registrar una mascota primero.")
        else:
            with st.form("appt_form"):
                pet_name = st.selectbox("Mascota", list(pet_options.keys()), key="appt_pet_select") # Added key
                date_val = st.date_input("Fecha")
                reason = st.text_area("Motivo de consulta")
                submit = st.form_submit_button("Agendar")
                
                if submit:
                    try:
                        service.book_appointment(pet_options[pet_name], date_val, reason)
                        st.success("Cita agendada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        st.subheader("Próximas Citas")
        if appts:
            # Transformar datos para visualización amigable
            data = []
            for a in appts:
                # Buscar nombre de mascota (en app real esto se haría con un JOIN en SQL)
                p_name = next((p.name for p in pets if p.id == a.pet_id), "Desconocido")
                data.append({"ID": a.id, "Fecha": a.date, "Mascota": p_name, "Motivo": a.reason, "Estado": a.status})
            
            df = pd.DataFrame(data)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            
            # --- SECCIÓN ELIMINAR CITA ---
            st.markdown("##### Eliminar Cita")
            appt_id_options = [a.id for a in appts]
            # CLAVE ÚNICA APLICADA: delete_appt_select_key
            appt_id_to_delete = st.selectbox("Seleccionar ID de Cita para eliminar", appt_id_options, key="delete_appt_select_key") 
            
            if st.button("🔴 Eliminar Cita", key="delete_appt_btn"):
                success = service.delete_appointment(appt_id_to_delete)
                if success:
                    st.warning(f"Cita ID {appt_id_to_delete} eliminada.")
                    st.rerun()
                else:
                    st.error("Error al eliminar la cita.")
                    
        else:
            st.info("No hay citas programadas")


def show_billing():
    st.header("💰 Gestión de Facturación")
    
    clients = service.list_clients()
    client_options = {f"{c.name} (ID: {c.id})": c.id for c in clients}
    client_id_to_name = {c.id: c.name for c in clients}
    
    col_generate, col_list = st.columns([1, 2])
    
    with col_generate:
        st.subheader("Generar Nueva Factura")
        if not clients:
            st.warning("Debes registrar clientes antes de generar facturas.")
        else:
            with st.form("new_invoice_form"):
                client_name_key = st.selectbox("Cliente", list(client_options.keys()), key="invoice_client_select")
                client_id = client_options[client_name_key]
                
                invoice_date = st.date_input("Fecha de Factura", value=date.today())
                total_amount = st.number_input("Monto Total (€)", min_value=0.01, step=5.00)
                
                submitted = st.form_submit_button("Emitir Factura")
                
                if submitted:
                    try:
                        service.generate_invoice(client_id, total_amount, invoice_date) 
                        st.success(f"Factura generada para {client_name_key}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al emitir factura: {e}")

    with col_list:
        st.subheader("Facturas Emitidas")
        invoices = service.list_invoices()
        
        if invoices:
            data = [vars(i) for i in invoices]
            df = pd.DataFrame(data)
            
            # Añadir nombre del cliente para visualización
            df['Cliente'] = df['client_id'].map(client_id_to_name)
            
            # Formato de tabla
            df = df.drop(columns=['client_id']).rename(columns={'id': 'ID', 'date': 'Fecha', 'total_amount': 'Monto', 'status': 'Estado'})
            
            st.dataframe(df, use_container_width=True)
            
        else:
            st.info("No hay facturas emitidas.")

def show_reviews():
    st.header("⭐ Gestión de Reseñas y Feedback")
    
    clients = service.list_clients()
    client_options = {f"{c.name} (ID: {c.id})": c.id for c in clients}
    client_id_to_name = {c.id: c.name for c in clients}
    
    col_submit, col_list = st.columns([1, 2])
    
    with col_submit:
        st.subheader("Enviar Reseña")
        if not clients:
            st.warning("Debes registrar clientes para enviar reseñas.")
        else:
            with st.form("new_review_form"):
                client_name_key = st.selectbox("Cliente que envía la reseña", list(client_options.keys()), key="review_client_select")
                client_id = client_options[client_name_key]
                
                rating = st.slider("Calificación", 1, 5, 5, key="review_rating")
                comment = st.text_area("Comentario", key="review_comment")
                
                submitted = st.form_submit_button("Enviar Feedback")
                
                if submitted:
                    try:
                        service.add_review(client_id, rating, comment) 
                        st.success(f"Reseña enviada por {client_name_key}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al enviar reseña: {e}")
                        
    with col_list:
        st.subheader("Reseñas Recibidas")
        reviews = service.list_reviews()
        
        if reviews:
            data = [vars(r) for r in reviews]
            df = pd.DataFrame(data)
            
            df['Cliente'] = df['client_id'].map(client_id_to_name)
            
            df = df.drop(columns=['client_id']).rename(columns={'id': 'ID', 'rating': 'Calificación', 'comment': 'Comentario', 'date': 'Fecha'})
            
            # Mostrar calificación con estrellas
            df['Calificación'] = df['Calificación'].apply(lambda x: "⭐" * x)

            st.dataframe(df, use_container_width=True)
            
            # Cálculo de promedio
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            st.markdown(f"**Promedio General:** {avg_rating:.2f} / 5")

        else:
            st.info("No hay reseñas registradas.")

if __name__ == "__main__":
    main()