import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Employee Attrition Intelligence", page_icon="📊", layout="wide")
st.title("📊 Employee Attrition Intelligence Dashboard")
st.caption("Diagnostic HR analytics | Explore attrition across teams, roles, demographics, tenure and workload")

@st.cache_data
def load_data():
    file = Path(__file__).parent / "data" / "employee_attrition.csv"
    data = pd.read_csv(file)
    # The supplied file encodes Attrition as 0 = retained and 1 = exited.
    data["AttritionLabel"] = data["Attrition"].map({0: "Retained", 1: "Exited"})
    data["AgeGroup"] = pd.cut(data["Age"], bins=[0, 25, 35, 45, 55, 100],
                             labels=["≤25", "26–35", "36–45", "46–55", "56+"])
    data["TenureBand"] = pd.cut(data["YearsAtCompany"], bins=[-1, 1, 5, 10, 100],
                               labels=["0–1 years", "2–5 years", "6–10 years", "11+ years"])
    return data

df = load_data()
with st.sidebar:
    st.header("Filters")
    departments = st.multiselect("Department", sorted(df["Department"].dropna().unique()), default=sorted(df["Department"].dropna().unique()))
    roles = st.multiselect("Job role", sorted(df["JobRole"].dropna().unique()), default=sorted(df["JobRole"].dropna().unique()))
    tenure_min, tenure_max = st.slider("Years at company", int(df.YearsAtCompany.min()), int(df.YearsAtCompany.max()),
                                      (int(df.YearsAtCompany.min()), int(df.YearsAtCompany.max())))
    overtime = st.multiselect("Overtime", sorted(df["OverTime"].dropna().unique()), default=sorted(df["OverTime"].dropna().unique()))
    travel = st.multiselect("Business travel", sorted(df["BusinessTravel"].dropna().unique()), default=sorted(df["BusinessTravel"].dropna().unique()))

f = df[
    df.Department.isin(departments) & df.JobRole.isin(roles) &
    df.YearsAtCompany.between(tenure_min, tenure_max) &
    df.OverTime.isin(overtime) & df.BusinessTravel.isin(travel)
].copy()

if f.empty:
    st.warning("No employees match the selected filters. Adjust the filters.")
    st.stop()

total = len(f)
exited = int(f.Attrition.sum())
retained = total - exited
rate = exited / total * 100
c1,c2,c3,c4 = st.columns(4)
c1.metric("Employees in view", f"{total:,}")
c2.metric("Exited employees", f"{exited:,}")
c3.metric("Retained employees", f"{retained:,}")
c4.metric("Attrition rate", f"{rate:.1f}%")

st.divider()
tab1,tab2,tab3,tab4 = st.tabs(["Overview","Department & role","Demographics & tenure","Workload & mobility"])

with tab1:
    left,right=st.columns(2)
    with left:
        counts=f["AttritionLabel"].value_counts().rename_axis("Status").reset_index(name="Employees")
        st.plotly_chart(px.pie(counts,names="Status",values="Employees",hole=.48,title="Retained vs exited"),use_container_width=True)
    with right:
        monthly=f.groupby("Department",as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
        monthly["Attrition rate (%)"]=monthly.Exits/monthly.Employees*100
        st.plotly_chart(px.bar(monthly,x="Department",y="Attrition rate (%)",text_auto=".1f",title="Attrition rate by department"),use_container_width=True)
    st.info("Rates are descriptive comparisons within the filtered employee population; they do not establish causation.")

with tab2:
    role=f.groupby(["Department","JobRole"],as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
    role["Attrition rate (%)"]=role.Exits/role.Employees*100
    st.plotly_chart(px.density_heatmap(role,x="JobRole",y="Department",z="Attrition rate (%)",histfunc="avg",
                                       title="Department × role attrition rate (%)",color_continuous_scale="Reds"),use_container_width=True)
    st.dataframe(role.sort_values("Attrition rate (%)",ascending=False).style.format({"Attrition rate (%)":"{:.1f}%"}),use_container_width=True)

with tab3:
    left,right=st.columns(2)
    with left:
        age=f.groupby("AgeGroup",observed=False,as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
        age["Attrition rate (%)"]=age.Exits/age.Employees*100
        st.plotly_chart(px.bar(age,x="AgeGroup",y="Attrition rate (%)",text_auto=".1f",title="Attrition by age group"),use_container_width=True)
    with right:
        tenure=f.groupby("TenureBand",observed=False,as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
        tenure["Attrition rate (%)"]=tenure.Exits/tenure.Employees*100
        st.plotly_chart(px.bar(tenure,x="TenureBand",y="Attrition rate (%)",text_auto=".1f",title="Attrition by company tenure"),use_container_width=True)
    st.subheader("Gender and marital status")
    a,b=st.columns(2)
    for col,container in [("Gender",a),("MaritalStatus",b)]:
        t=f.groupby(col,as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
        t["Attrition rate (%)"]=t.Exits/t.Employees*100
        container.plotly_chart(px.bar(t,x=col,y="Attrition rate (%)",text_auto=".1f",title=f"Attrition by {col}"),use_container_width=True)

with tab4:
    a,b=st.columns(2)
    for col,container in [("OverTime",a),("BusinessTravel",b)]:
        t=f.groupby(col,as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
        t["Attrition rate (%)"]=t.Exits/t.Employees*100
        container.plotly_chart(px.bar(t,x=col,y="Attrition rate (%)",text_auto=".1f",title=f"Attrition by {col}"),use_container_width=True)
    dist=f.copy()
    dist["DistanceBand"]=pd.cut(dist.DistanceFromHome,bins=[-1,5,10,20,1000],labels=["0–5","6–10","11–20","21+"])
    t=dist.groupby("DistanceBand",observed=False,as_index=False).agg(Employees=("Attrition","size"),Exits=("Attrition","sum"))
    t["Attrition rate (%)"]=t.Exits/t.Employees*100
    st.plotly_chart(px.bar(t,x="DistanceBand",y="Attrition rate (%)",text_auto=".1f",title="Attrition by distance from home"),use_container_width=True)

st.divider()
st.subheader("Filtered employee records")
st.dataframe(f.drop(columns=["AttritionLabel","AgeGroup","TenureBand"]),use_container_width=True,hide_index=True)
st.download_button("Download filtered data (CSV)", f.drop(columns=["AttritionLabel","AgeGroup","TenureBand"]).to_csv(index=False),
                   file_name="filtered_employee_attrition.csv",mime="text/csv")
st.caption("Dataset provided by the project requester. The dashboard treats Attrition 1 as Exited and 0 as Retained.")
