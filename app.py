import streamlit as st
import pandas as pd
from src.database import DatabaseManager
from src.repositories import ClientRepository, PetRepository, AppointmentRepository
from src.services import ClinicService
from src.models import Client, Pet, Appointment # Importamos los modelos

# --- Inyección de Dependencias (Composition Root) ---
db = DatabaseManager()
db.initialize_db()

client_repo = ClientRepository(db)
pet_repo = PetRepository(db)
appt_repo = AppointmentRepository(db)
service = ClinicService(client_repo, pet_repo, appt_repo)

# Carga datos de prueba si está vacío
service.seed_data()

# --- Configuración de la Página ---
st.set_page_config(page_title="VetManager Pro", layout="wide", page_icon="🐾")

# --- UI Styling & Estructura ---
def main():
    st.sidebar.title("🐾 VetManager")
    menu = st.sidebar.radio("Navegación", ["Inicio", "Clientes", "Mascotas", "Calendario & Citas"])

    if menu == "Inicio":
        show_home()
    elif menu == "Clientes":
        show_clients()
    elif menu == "Mascotas":
        show_pets()
    elif menu == "Calendario & Citas":
        show_calendar()

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
    
    # --- Columna de Registro ---
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

    # Listado de clientes
    clients = service.list_clients()
    client_df = pd.DataFrame([vars(c) for c in clients])
    
    col_list, col_actions = st.columns([2, 1])

    with col_list:
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
    
    # Necesitamos clientes para asociar mascota
    clients = service.list_clients()
    client_options = {c.name: c.id for c in clients}
    
    col_register, col_actions = st.columns(2)
    
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

   # app.py (Corregido, alrededor de la línea 226)

    pets = service.list_pets()
    
    # Mapeo de IDs de cliente a nombres de cliente
    client_id_to_name = {c.id: c.name for c in clients}

    # FILTRAR: Solo incluimos mascotas cuyo dueño (client_id) existe en la lista de clientes.
    valid_pets = [p for p in pets if p.client_id in client_id_to_name]
    
    pet_df = pd.DataFrame([vars(p) for p in pets])
    
    with col_actions:
        st.subheader("Listado de Mascotas")
        if not pets:
            st.info("No hay mascotas registradas.")
        else:
            st.dataframe(pet_df, use_container_width=True)
            
            # --- SECCIÓN EDITAR MASCOTA ---
            st.divider()
            st.markdown("##### Editar Mascota")
            
            if not valid_pets:
                st.warning("No hay mascotas con dueños válidos para editar.")
            else:
                pet_options = {f"{p.name} (ID: {p.id})": p for p in valid_pets}
                
                pet_to_edit_key = st.selectbox("Seleccionar Mascota para editar", 
                                               list(pet_options.keys()), 
                                               key="edit_pet_select")
                pet_to_edit = pet_options[pet_to_edit_key]
                
                # Obtener el nombre actual del dueño usando el mapeo
                current_owner_name = client_id_to_name.get(pet_to_edit.client_id)
                
                # Encontrar el índice del dueño actual en la lista de selección
                owner_names_list = list(client_options.keys())
                current_owner_index = owner_names_list.index(current_owner_name)

                with st.form("edit_pet_form"):
                    st.markdown(f"**Editando ID:** {pet_to_edit.id}")
                    edit_name = st.text_input("Nombre Mascota", value=pet_to_edit.name)
                    
                    species_list = ["Perro", "Gato", "Ave", "Roedor", "Otro"]
                    current_species_index = species_list.index(pet_to_edit.species)
                    edit_species = st.selectbox("Especie", species_list, index=current_species_index)
                    
                    edit_breed = st.text_input("Raza", value=pet_to_edit.breed)
                    edit_age = st.number_input("Edad", min_value=0, value=pet_to_edit.age, step=1)
                    
                    # Usar current_owner_index para establecer el valor inicial del selectbox del Dueño
                    edit_owner_name = st.selectbox("Dueño", owner_names_list, index=current_owner_index)
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
                pet_name = st.selectbox("Mascota", list(pet_options.keys()))
                date_val = st.date_input("Fecha")
                reason = st.text_area("Motivo de consulta")
                submit = st.form_submit_button("Agendar")
                
                if submit:
                    try:
                        service.book_appointment(pet_options[pet_name], str(date_val), reason)
                        st.success("Cita agendada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        st.subheader("Próximas Citas")
        if appts:
            # Transformar datos para visualización amigable
            data = []
            appt_lookup = {a.id: a for a in appts}
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
            appt_id_to_delete = st.selectbox("Seleccionar ID de Cita para eliminar", appt_id_options, key="delete_appt_select")
            
            if st.button("🔴 Eliminar Cita", key="delete_appt_btn"):
                success = service.delete_appointment(appt_id_to_delete)
                if success:
                    st.warning(f"Cita ID {appt_id_to_delete} eliminada.")
                    st.rerun()
                else:
                    st.error("Error al eliminar la cita.")
                    
        else:
            st.info("No hay citas programadas")


if __name__ == "__main__":
    main()