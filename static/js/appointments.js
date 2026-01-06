(function () {
  const deptSelect = document.querySelector('select[name="department"]');
  const doctorSelect = document.querySelector('select[name="preferred_doctor"]');
  if (!deptSelect || !doctorSelect) return;

  const initialDoctorValue = doctorSelect.value;

  function setOptions(doctors) {
    const current = doctorSelect.value;
    const placeholder = doctorSelect.querySelector('option[value=""]');
    doctorSelect.innerHTML = "";
    const emptyOpt = document.createElement("option");
    emptyOpt.value = "";
    emptyOpt.textContent = placeholder ? placeholder.textContent : "No preference";
    doctorSelect.appendChild(emptyOpt);
    doctors.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = String(d.id);
      opt.textContent = `${d.full_name} — ${d.specialization}`;
      doctorSelect.appendChild(opt);
    });
    if (current && doctorSelect.querySelector(`option[value="${CSS.escape(current)}"]`)) {
      doctorSelect.value = current;
    }
  }

  async function refreshDoctors() {
    const deptId = deptSelect.value;
    if (!deptId) {
      setOptions([]);
      return;
    }
    try {
      const res = await fetch(`/appointments/doctors/?department_id=${encodeURIComponent(deptId)}`, {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error("Bad response");
      const data = await res.json();
      setOptions(Array.isArray(data.doctors) ? data.doctors : []);
    } catch (e) {
      setOptions([]);
    }
  }

  deptSelect.addEventListener("change", function () {
    doctorSelect.value = "";
    refreshDoctors();
  });

  refreshDoctors().then(() => {
    if (initialDoctorValue) {
      const exists = doctorSelect.querySelector(`option[value="${CSS.escape(initialDoctorValue)}"]`);
      if (exists) doctorSelect.value = initialDoctorValue;
    }
  });
})();

