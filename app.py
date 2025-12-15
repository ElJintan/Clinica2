import streamlit as st
import pandas as pd
from src.database import DatabaseManager
from src.repositories import ClientRepository, PetRepository, AppointmentRepository
from src.services import ClinicService

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

    # Listado
    clients = service.list_clients()
    if clients:
        df = pd.DataFrame([vars(c) for c in clients])
        st.dataframe(df, use_container_width=True)
        
        # Eliminar
        st.divider()
        st.subheader("Acciones")
        c_id = st.selectbox("Seleccionar ID Cliente para eliminar", [c.id for c in clients])
        if st.button("Eliminar Cliente"):
            service.delete_client(c_id)
            st.warning("Cliente eliminado")
            st.rerun()

def show_pets():
    st.header("Gestión de Mascotas")
    
    # Necesitamos clientes para asociar mascota
    clients = service.list_clients()
    client_options = {c.name: c.id for c in clients}
    
    with st.expander("➕ Registrar Nueva Mascota"):
        with st.form("new_pet"):
            name = st.text_input("Nombre Mascota")
            species = st.selectbox("Especie", ["Perro", "Gato", "Ave", "Roedor", "Otro"])
            breed = st.text_input("Raza")
            age = st.number_input("Edad", min_value=0)
            owner_name = st.selectbox("Dueño", list(client_options.keys()))
            
            submitted = st.form_submit_button("Guardar Mascota")
            if submitted:
                service.add_pet(name, species, breed, age, client_options[owner_name])
                st.success("Mascota añadida")
                st.rerun()
    
    pets = service.list_pets()
    if pets:
        df = pd.DataFrame([vars(p) for p in pets])
        st.dataframe(df, use_container_width=True)

def show_calendar():
    st.header("📅 Calendario de Citas")
    
    pets = service.list_pets()
    pet_options = {f"{p.name} ({p.species})": p.id for p in pets}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Agendar Cita")
        with st.form("appt_form"):
            pet_name = st.selectbox("Mascota", list(pet_options.keys()))
            date_val = st.date_input("Fecha")
            reason = st.text_area("Motivo de consulta")
            submit = st.form_submit_button("Agendar")
            
            if submit:
                service.book_appointment(pet_options[pet_name], date_val, reason)
                st.success("Cita agendada")
                st.rerun()

    with col2:
        st.subheader("Próximas Citas")
        appts = service.list_appointments()
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
        else:
            st.info("No hay citas programadas")

if __name__ == "__main__":
    main()