import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Judul aplikasi
st.title("Advanced Data Visualization Tool")

BASE_URL = "https://satudata.jatengprov.go.id/v1/data/"
BASE_URL1 = "https://satudata.jatengprov.go.id/v1/data?page="
TOKEN = "8D7xcIj1JPfsHYctqe0twPABS67_kKm0"  # Token dalam tanda kutip
filtered_df = None
filtered_df2 = None
df = None
data = None

# Fungsi untuk mengubah tipe data
def modify_column_dtype(df, column, new_dtype):
    try:
        if new_dtype == "String":
            df[column] = df[column].astype(str)
        elif new_dtype == "Integer":
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype('int64')
        elif new_dtype == "Float":
            df[column] = pd.to_numeric(df[column], errors="coerce")
        elif new_dtype == "Datetime":
            df[column] = pd.to_datetime(df[column], errors="coerce")
        elif new_dtype == "Boolean":
            df[column] = df[column].astype(bool)


# Fungsi untuk memfilter data dengan banyak filter opsional
def apply_filters(df):
    st.sidebar.header("Filters (Optional)")
    filter_count = st.sidebar.number_input("Number of Filters", min_value=0, max_value=10, step=1, value=0, key="filter_count")

    for i in range(filter_count):
        st.sidebar.subheader(f"Filter {i + 1}")
        filter_column = st.sidebar.selectbox(f"Select Column for Filter {i + 1}", df.columns, key=f"filter_col_{i}")

        if pd.api.types.is_numeric_dtype(df[filter_column]):
            min_val = float(df[filter_column].min())
            max_val = float(df[filter_column].max())
            selected_range = st.sidebar.slider(
                f"Select Range for {filter_column}",
                min_val, max_val, (min_val, max_val), key=f"slider_{i}"
            )
            df = df[df[filter_column].between(selected_range[0], selected_range[1])]
        else:
            unique_values = df[filter_column].dropna().unique()
            selected_values = st.sidebar.multiselect(
                f"Select Values for {filter_column}",
                unique_values, key=f"filter_val_{i}"
            )
            if selected_values:
                df = df[df[filter_column].isin(selected_values)]

    return df


def apply_filters2(df):
    st.sidebar.header("Filters (Optional)")
    filter_count2 = st.sidebar.number_input("Number of Filters", min_value=0, max_value=10, step=1, value=0, key="filter_count2")

    for i in range(filter_count2):
        st.sidebar.subheader(f"Filter {i + 1}")
        filter_column2 = st.sidebar.selectbox(f"Select Column for Filter {i + 1}", df.columns, key=f"filter2_col_{i}")

        if pd.api.types.is_numeric_dtype(df[filter_column2]):
            min_val = float(df[filter_column2].min())
            max_val = float(df[filter_column2].max())
            selected_range = st.sidebar.slider(
                f"Select Range for {filter_column2}",
                min_val, max_val, (min_val, max_val), key=f"slider2_{i}"
            )
            df = df[df[filter_column2].between(selected_range[0], selected_range[1])]
        else:
            unique_values = df[filter_column2].dropna().unique()
            selected_values = st.sidebar.multiselect(
                f"Select Values for {filter_column2}",
                unique_values, key=f"filter2_val_{i}"
            )
            if selected_values:
                df = df[df[filter_column2].isin(selected_values)]

    return df


def fetch_and_convert_to_dataframe(url, token):
    """
    Mengambil data dari API dan mengubahnya menjadi DataFrame.

    Args:
    - url (str): URL untuk melakukan permintaan GET.
    - token (str): Token untuk otentikasi.

    Returns:
    - pd.DataFrame: DataFrame yang berisi data dari respons API, atau None jika gagal.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # Mengirim permintaan GET ke URL
    response = requests.get(url, headers=headers)

    # Cek status kode untuk memastikan respons berhasil
    if response.status_code == 200:
        # Mengambil data JSON dari respons
        data = response.json()

        # Cek struktur data JSON untuk menemukan array yang berisi data yang akan diubah menjadi DataFrame
        if isinstance(data, dict) and 'data' in data:
            # Jika data ada dalam dictionary dengan key 'data', ambil nilai tersebut
            data_list = data['data']
            
            # Ubah list of dictionaries menjadi DataFrame
            df = pd.DataFrame(data_list)
            
            # Mengembalikan DataFrame sebagai hasil
            return df
        else:
            st.error("Tidak ada data dalam respons JSON.")
            return None
    else:
        # Tampilkan pesan error jika gagal
        st.error(f"Failed to fetch data. Status Code: {response.status_code}")
        st.error("Response: " + response.text)
        return None
    
# Upload file pertama atau ambil dari API
# Komponen sidebar

st.sidebar.header("Data from API")

headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.get(BASE_URL, headers=headers)
data = response.json()
pageCount = data['_meta']['pageCount']

@st.cache_data
def fetch_all_data(base_url, token, page_count):
    data = None
    for i in range(1, page_count):
        new_url = f"{base_url}{i}"
        data_T = fetch_and_convert_to_dataframe(new_url, token)
        data = pd.concat([data, data_T], ignore_index=True)
    return data

# Ambil data
data = fetch_all_data(BASE_URL1, TOKEN, pageCount)


# Inisialisasi state untuk menyimpan tipe data yang diubah dan judul yang dipilih
if "column_dtypes" not in st.session_state:
    st.session_state.column_dtypes = {}
if "current_judul" not in st.session_state:
    st.session_state.current_judul = None

# Jika ada data untuk ditampilkan
if data is not None:
    # Menampilkan opsi untuk memilih judul dari kolom "judul"
    judul_selected = st.sidebar.selectbox(
        "Pilih Judul",
        options=[None] + list(data['judul'].unique()),
        index=0
    )

    # Reset state jika judul berubah
    if judul_selected != st.session_state.current_judul:
        st.session_state.column_dtypes = {}  # Reset tipe data yang diubah
        st.session_state.current_judul = judul_selected  # Perbarui judul yang dipilih

    if judul_selected is not None:
        # Mendapatkan ID berdasarkan judul yang dipilih
        id_selected = data[data['judul'] == judul_selected]['id'].iloc[0]
        # Menambahkan kata "id" ke akhir URL
        new_url = f"{BASE_URL.rstrip('/')}/{id_selected}"
        # Mengambil data berdasarkan ID yang dipilih
        df = fetch_and_convert_to_dataframe(new_url, TOKEN)

        if df is not None:
            st.sidebar.header(f"Modify Column Data Types")

            # Pilih kolom untuk dimodifikasi
            column_to_modify = st.sidebar.selectbox("Select Column to Modify", df.columns, key="col")

            # Pilih tipe data baru
            new_data_type = st.sidebar.selectbox(
                "Select New Data Type",
                ["No Change", "String", "Integer", "Float", "Datetime", "Boolean"],
                index=0,
                key="dtype"
            )

            # Simpan tipe data baru ke dalam session state
            if new_data_type != "No Change":
                st.session_state.column_dtypes[column_to_modify] = new_data_type
                modify_column_dtype(df, column_to_modify, new_data_type)

            # Terapkan perubahan tipe data berdasarkan session state
            for column, dtype in st.session_state.column_dtypes.items():
                modify_column_dtype(df, column, dtype)

            # Terapkan filter dan tampilkan data
            filtered_df = apply_filters(df)
            st.write("### Preview Data")
            st.write(f"##### {judul_selected}")
            st.dataframe(filtered_df)
        else:
            st.write("No data available to display.")
    else:
        st.write("Please select a title to display data.")

        
# Halaman visualisasi
pages = ["Single Dataset Visualization", "Double Dataset Visualization"]
selected_page = st.sidebar.selectbox("Select Page", pages)

if selected_page == "Single Dataset Visualization" and df is not None:
    st.header("Visualize Single Dataset")
    
    numeric_columns = filtered_df.select_dtypes(include=['float64', 'int64']).columns
    categorical_columns = filtered_df.select_dtypes(include=['object']).columns

    st.sidebar.header("Graph Options")
    graph_type = st.sidebar.selectbox("Select Graph Type", ["Bar Chart", "Scatter Plot", "Line Chart", "Pie Chart"])

    if graph_type == "Bar Chart":
        x_col = st.sidebar.selectbox("X-axis", categorical_columns)
        y_col = st.sidebar.selectbox("Y-axis", numeric_columns)
        agg_function = st.sidebar.selectbox("Aggregation Type", ["None", "Sum", "Count", "Mean", "Median", "Max", "Min"])
        color = st.sidebar.color_picker("Select Bar Chart Color", "#636EFA")

        # Tambahkan input untuk label sumbu dengan default nama kolom
        title_label = st.sidebar.text_input("Custom Title Chart", value=f"{agg_function} of {y_col} by {x_col}")

        if agg_function == "None":
            fig = px.bar(
                filtered_df, 
                x=x_col, 
                y=y_col, 
                title=title_label, 
                color_discrete_sequence=[color], 
                labels={"x": x_col, "y": y_col}
            )
        else:
            agg_map = {
                "Sum": "sum",
                "Count": "count",
                "Mean": "mean",
                "Median": "median",
                "Max": "max",
                "Min": "min"
            }
            aggregated_data = filtered_df.groupby(x_col)[y_col].agg(agg_map[agg_function]).reset_index()
            fig = px.bar(
                aggregated_data, 
                x=x_col, 
                y=y_col, 
                title=title_label, 
                color_discrete_sequence=[color],
                labels={"x": x_col, "y": y_col}
            )
        
        st.plotly_chart(fig)

    elif graph_type == "Scatter Plot":
        x_col = st.sidebar.selectbox("X-axis", numeric_columns)
        y_col = st.sidebar.selectbox("Y-axis", numeric_columns)
        color_by = st.sidebar.selectbox("Color By (Optional)", [None] + list(categorical_columns), index=0)

        # Tambahkan input untuk label sumbu dengan default nama kolom
        title_label = st.sidebar.text_input("Custom Title Chart", value=f"Scatter Plot of {x_col} vs {y_col}" + (f" by {color_by}" if color_by else ""))

        fig = px.scatter(
            filtered_df, 
            x=x_col, 
            y=y_col, 
            color=color_by, 
            title=title_label,
            labels={"x": x_col, "y": y_col}
        )
        st.plotly_chart(fig)

    elif graph_type == "Line Chart":
        x_col = st.sidebar.selectbox("X-axis", numeric_columns)
        y_col = st.sidebar.selectbox("Y-axis", numeric_columns)
        color = st.sidebar.color_picker("Select Line Chart Color", "#636EFA")

        # Tambahkan input untuk label sumbu dengan default nama kolom
        title_label = st.sidebar.text_input("Custom Title Chart", value=f"Line Chart of {x_col} vs {y_col}")

        fig = px.line(
            filtered_df, 
            x=x_col, 
            y=y_col, 
            title=title_label, 
            color_discrete_sequence=[color],
            labels={"x": x_col, "y": y_col}
        )
        st.plotly_chart(fig)

    elif graph_type == "Pie Chart":
        category_col = st.sidebar.selectbox("Category Column", categorical_columns)
        
        # Tambahkan opsi "Count" ke daftar kolom numerik
        value_options = ["Count"] + list(numeric_columns)
        value_col = st.sidebar.selectbox("Value Column", value_options)
        
        color = st.sidebar.color_picker("Select Pie Chart Color", "#636EFA")
        title_label = st.sidebar.text_input(f"Pie Chart of {category_col}")

        # Tentukan nilai untuk pie chart
        if value_col == "Count":
            # Menghitung jumlah kategori terlebih dahulu
            category_counts = filtered_df[category_col].value_counts().reset_index()
            category_counts.columns = [category_col, 'Count']

            # Membuat diagram pie
            fig = px.pie(
                category_counts,
                names=category_col,
                values='Count',
                title=title_label,
                color_discrete_sequence=[color]
            )
        else:
            fig = px.pie(
                filtered_df,
                names=category_col,
                values=value_col,
                title=title_label,
                color_discrete_sequence=[color]
            )
        
        # Tampilkan pie chart
        st.plotly_chart(fig)


elif selected_page == "Double Dataset Visualization":
    st.header("Visualize Correlation Between Two Datasets")
    
    # Upload dataset kedua
    # Inisialisasi state untuk menyimpan tipe data yang diubah dan judul yang dipilih
    if "column_dtypes2" not in st.session_state:
        st.session_state.column_dtypes2 = {}
    if "current_judul2" not in st.session_state:
        st.session_state.current_judul2 = None

    # Jika ada data untuk ditampilkan
    if data is not None:
        # Menampilkan opsi untuk memilih judul dari kolom "judul"
        judul_selected2 = st.selectbox(
            "Pilih Judul",
            options=[None] + list(data['judul'].unique()),
            index=0,
            key="JudulSelect2"
        )

        # Reset state jika judul berubah
        if judul_selected2 != st.session_state.current_judul2:
            st.session_state.column_dtypes2 = {}  # Reset tipe data yang diubah
            st.session_state.current_judul2 = judul_selected2  # Perbarui judul yang dipilih

        if judul_selected2 is not None:
            # Mendapatkan ID berdasarkan judul yang dipilih
            id_selected = data[data['judul'] == judul_selected2]['id'].iloc[0]
            # Menambahkan kata "id" ke akhir URL
            new_url = f"{BASE_URL.rstrip('/')}/{id_selected}"
            # Mengambil data berdasarkan ID yang dipilih
            df2 = fetch_and_convert_to_dataframe(new_url, TOKEN)

            if df2 is not None:
                st.sidebar.header(f"Modify Column Data Types 2")

                # Pilih kolom untuk dimodifikasi
                column_to_modify = st.sidebar.selectbox("Select Column to Modify", df2.columns, key="col2")

                # Pilih tipe data baru
                new_data_type = st.sidebar.selectbox(
                    "Select New Data Type",
                    ["No Change", "String", "Integer", "Float", "Datetime", "Boolean"],
                    index=0,
                    key="dtype2"
                )

                # Simpan tipe data baru ke dalam session state
                if new_data_type != "No Change":
                    st.session_state.column_dtypes2[column_to_modify] = new_data_type
                    modify_column_dtype(df2, column_to_modify, new_data_type)

                # Terapkan perubahan tipe data berdasarkan session state
                for column, dtype2 in st.session_state.column_dtypes2.items():
                    modify_column_dtype(df2, column, dtype2)

                # Terapkan filter dan tampilkan data
                filtered_df2 = apply_filters2(df2)

                st.write("### Preview Data")
                st.write(f"##### {judul_selected2}")
                st.dataframe(filtered_df2)
            else:
                st.write("No data available to display.")

        if filtered_df is not None and filtered_df2 is not None:
            numeric_columns1 = filtered_df.select_dtypes(include=['float64', 'int64']).columns
            categorical_columns1 = filtered_df.select_dtypes(include=['object']).columns

            numeric_columns2 = filtered_df2.select_dtypes(include=['float64', 'int64']).columns
            categorical_columns2 = filtered_df2.select_dtypes(include=['object']).columns
            # Visualisasi korelasi dengan kemampuan memilih dataset untuk X dan Y
            if len(filtered_df) != len(filtered_df2):
                st.warning(f"The two datasets must have the same number of rows! Dataset 1 rows: {len(filtered_df)}, Dataset 2 rows: {len(filtered_df2)}")
            else:
                st.sidebar.header("Correlation Graph Options")

                # Pilih dataset untuk x-axis
                x_axis_dataset = st.sidebar.radio("Select Dataset for X-axis", ["Dataset 1", "Dataset 2"], key="x_axis_dataset")
                if x_axis_dataset == "Dataset 1":
                    x_col = st.sidebar.selectbox("Select X-axis Column (Dataset 1)", numeric_columns1, key="x_axis_col1")
                    x_data = filtered_df[x_col]
                else:
                    x_col = st.sidebar.selectbox("Select X-axis Column (Dataset 2)", numeric_columns2, key="x_axis_col2")
                    x_data = filtered_df2[x_col]

                # Pilih dataset untuk y-axis
                y_axis_dataset = st.sidebar.radio("Select Dataset for Y-axis", ["Dataset 1", "Dataset 2"], key="y_axis_dataset")
                if y_axis_dataset == "Dataset 1":
                    y_col = st.sidebar.selectbox("Select Y-axis Column (Dataset 1)", numeric_columns1, key="y_axis_col1")
                    y_data = filtered_df[y_col]
                else:
                    y_col = st.sidebar.selectbox("Select Y-axis Column (Dataset 2)", numeric_columns2, key="y_axis_col2")
                    y_data = filtered_df2[y_col]

                # Pilih jenis grafik
                graph_type = st.sidebar.selectbox("Select Graph Type for Correlation", ["Scatter Plot", "Line Chart", "Bar Chart"])

                # Perhitungan korelasi
                combined_data = pd.DataFrame({x_col: x_data, y_col: y_data}).dropna()
                correlation = combined_data[x_col].corr(combined_data[y_col])
                correlation_text = f"Correlation: {correlation:.2f}"

                # Buat grafik berdasarkan jenis yang dipilih
                if graph_type == "Scatter Plot":
                    title_label = st.sidebar.text_input("Custom Title Chart", value=f"Scatter Plot of {x_col} vs {y_col}")
                    fig = px.scatter(
                        x=x_data, 
                        y=y_data, 
                        title=title_label, 
                        labels={"x": x_col, "y": y_col}
                    )
                elif graph_type == "Line Chart":
                    title_label = st.sidebar.text_input("Custom Title Chart", value=f"Line Chart of {x_col} vs {y_col}")
                    fig = px.line(
                        x=x_data, 
                        y=y_data, 
                        title=title_label, 
                        labels={"x": x_col, "y": y_col}
                    )
                elif graph_type == "Bar Chart":
                    title_label = st.sidebar.text_input("Custom Title Chart", value=f"Bar Chart of {x_col} vs {y_col}")
                    combined_data = pd.DataFrame({x_col: x_data, y_col: y_data})
                    fig = px.bar(
                        combined_data, 
                        x=x_col, 
                        y=y_col, 
                        title=title_label,
                        labels={"x": x_col, "y": y_col}
                    )

                # Tampilkan grafik
                st.plotly_chart(fig)

                # Tampilkan nilai korelasi di bawah grafik
                st.markdown(f"### {correlation_text}")
        else:
            st.write("Please select a title to display data.")
