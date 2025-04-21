# --- Imports ---
import panel as pn
import panel.template as pnt
import time, threading, atexit
import numpy as np, datetime
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import TapTool, HoverTool
import asyncio # For async callback
from bokeh import palettes # For colormaps
import matplotlib.pyplot as plt # Import Matplotlib
import random # For simulation variation

#################################################################
# Style --------------------------------------------------------
#################################################################

# --- Custom CSS for Navigation ---
custom_nav_css_scoped = """
/* Add margin to the host element itself */
:host {
  display: block; /* Ensure margin works */
  margin-top: 5px;
}

/* Style the unordered list directly */
ul {
  list-style-type: none; /* Remove bullets */
  padding-left: 0;       /* Remove default padding */
  margin-bottom: 0;      /* Remove default bottom margin */
  margin-top: 0;         /* Remove potential top margin */
}

/* Style each list item */
li {
  margin-bottom: 4px; /* Add space between items */
}

/* Style the links within list items */
li a {
  display: block; /* Make the entire area clickable */
  padding: 8px 15px; /* Add padding inside the link */
  text-decoration: none; /* Remove underline */
  color: #333; /* Dark grey text color */
  border-radius: 4px; /* Slightly rounded corners */
  transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out; /* Smooth transition */
  font-size: 0.95em; /* Slightly smaller font */
}

/* Style links on hover */
li a:hover {
  background-color: #e9ecef; /* Light grey background on hover */
  color: #0056b3; /* Darker blue text on hover */
}

/* Style for active/clicked link (optional) */
/* We will replace this with the .active class style */
/* li a:active {
   background-color: #ced4da; /* Slightly darker background when clicked */
/* } */

/* --- NEW: Style for the active link --- */
li a.active {
  background-color: #1f77b4; /* Use the SELECTED_COLOR */
  color: white;             /* White text for contrast */
  font-weight: bold;        /* Make it bold */
}

/* Optional: Keep active style even on hover */
li a.active:hover {
  background-color: #1f77b4; /* Keep background */
  color: white;             /* Keep text color */
}
"""

# --- Panel Extensions and Theme ---
# Apply CSS via stylesheets parameter on component, not here
pn.extension(sizing_mode="fixed")

# --- Configuration ---
GRID_SIZE = 16
DEFAULT_COLOR = "lightgrey"
SELECTED_COLOR = "#1f77b4"
FULL_SCAN_VMIN = -1.0; FULL_SCAN_VMAX = 1.0; FULL_SCAN_STEP = 0.05; FULL_SCAN_GATE = 0.0
CONDUCTANCE_VOLTAGE = 0.1; MIN_CONDUCTANCE = 0.1; MAX_CONDUCTANCE = 1.5
COLOR_PALETTE = palettes.Viridis256

# --- Global Simulation State ---
device_states = {} # Use dict for standalone simulation state

#################################################################
# --- Server Initialization & Cleanup ---
#################################################################

server_start_time = datetime.datetime.now()
print(f"Script loaded at: {server_start_time}")

# --- KEEPING USER'S VERSION OF initialize_server_resources ---
def initialize_server_resources():
    """Function called once when the Panel server loads the app."""
    print(f"--- Server Initialization ({datetime.datetime.now()}) ---")
    # Example: Load a large data file, initialize hardware connection (placeholder)
    pn.state.cache['server_start_time'] = server_start_time
    pn.state.cache['global_config'] = {"status": "Initialized", "version": "1.1"} # User version had 1.1

    if not hasattr(pn.state, '_server_initialized'):
        print("--- Running Server Initialization ---")
        pn.state.cache['shared_resource'] = f"Resource Loaded at Startup {time.time():.2f}"
        pn.state._server_initialized = True
        print("--- Server Initialization Complete---") # User had triple dash


    print("Global resources initialized.")
    # Note: Objects stored in pn.state.cache here are shared across all sessions
# --- END OF USER'S VERSION ---

def cleanup_on_exit():
    """Function called when the Python process exits."""
    print(f"\n--- Server Shutting Down ({datetime.datetime.now()}) ---")
    print("Performing cleanup tasks...")
    print("Cleanup complete. Server exiting.")

# Register the functions
pn.state.onload(initialize_server_resources)
atexit.register(cleanup_on_exit)


# --- Simulation Function ---
def simulate_iv_curve(row, col, vmin, vmax, step, gate_v):
    """Generates I-V curve data using measurement parameters."""
    print(f"Simulating R{row}C{col}: Vmin={vmin}, Vmax={vmax}, Step={step}, Gate={gate_v}")
    if step == 0: step = 0.01
    num_points = int(np.floor((vmax - vmin) / step)) + 1
    voltage = np.linspace(vmin, vmin + (num_points - 1) * step, num_points)
    voltage = np.clip(voltage, vmin, vmax)
    resistance = 1 + (row + col * GRID_SIZE) / (GRID_SIZE*GRID_SIZE*1.5)
    gate_factor = 1 + gate_v * 0.1
    current = (voltage / (resistance * gate_factor)) + np.random.normal(0, 0.05, size=voltage.shape)
    threshold = 0.5 + (row % 4) * 0.1
    current[np.abs(voltage) > threshold] *= (1.1 + gate_v * 0.05)
    return dict(voltage=voltage.tolist(), current=current.tolist())


# --- Standalone Hardware Simulation Functions ---
def apply_voltage_pulse(row, col, amplitude_v, width_s):
    global device_states
    print(f"HW_SIM: Applying {amplitude_v:.3f} V, {width_s*1e6:.1f} us pulse to R{row}C{col}")
    key = f'device_state_R{row}C{col}'
    current_factor = device_states.get(key, 10.0)
    base_change_factor = 0.05
    if amplitude_v > 0:
        change = base_change_factor * abs(amplitude_v) * (current_factor - 0.05)
        device_states[key] = max(0.1, current_factor - change)
    elif amplitude_v < 0:
        change = base_change_factor * abs(amplitude_v) * (15.0 - current_factor)
        device_states[key] = min(20.0, current_factor + change)
    print(f"HW_SIM: State factor for R{row}C{col} updated to {device_states.get(key, 'N/A'):.4f}")
    time.sleep(0.005)
    return True

def read_resistance(row, col, read_voltage_v):
    global device_states
    key = f'device_state_R{row}C{col}'
    internal_state_factor = device_states.get(key, 10.0)
    base_resistance = 10e3
    simulated_r = base_resistance * internal_state_factor
    read_noise = simulated_r * np.random.normal(0, 0.01)
    final_r = simulated_r + read_noise
    # Intentionally kept verbose print for debugging as in user's code
    print(f"HW_SIM: Reading R{row}C{col} (Vread={read_voltage_v:.3f} V)... Sim R = {final_r:.2f} Ohms")
    time.sleep(0.01)
    if not np.isfinite(final_r) or final_r <= 0:
        print(f"Warning: Invalid resistance reading ({final_r})")
        return None
    return final_r

#################################################################
# --- Bokeh Plot and CDS Creation ---
#################################################################
def create_grid_cds(size=GRID_SIZE):
    x_coords = np.arange(size) + 0.5
    y_coords = np.arange(size) + 0.5
    xx, yy = np.meshgrid(x_coords, y_coords)
    grid_x = xx.ravel()
    grid_y = yy.ravel()
    colors = [DEFAULT_COLOR] * (size * size)
    rows = np.floor(grid_y - 0.5).astype(int)
    cols = np.floor(grid_x - 0.5).astype(int)
    ids = [f"R{r}C{c}" for r, c in zip(rows, cols)]
    return ColumnDataSource(data=dict(x=grid_x, y=grid_y, color=colors, row=rows, col=cols, id=ids))

def create_selector_plot(source, size=GRID_SIZE):
    hover = HoverTool(tooltips=[("Device", "@id"), ("Row", "@row"), ("Col", "@col")])
    tools = [TapTool(), hover, "pan", "wheel_zoom", "reset"]
    p = figure(height=250, width=250, # Reduced size for footer
               tools=tools, title="Device Grid",
               x_range=(0, size), y_range=(0, size),
               x_axis_location=None, y_axis_location=None,
               toolbar_location=None, match_aspect=True,
               min_border=0, outline_line_color=None)
    p.grid.visible = False
    p.rect(x='x', y='y', width=1, height=1, source=source,
           fill_color='color', line_color="white", line_width=1)
    tap_tool = p.select(type=TapTool)
    tap_tool.behavior = "select"
    return p

def create_iv_cds():
    return ColumnDataSource(data=dict(voltage=[], current=[]))

def create_iv_plot(source):
    p = figure(height=400, # Initial height, will stretch
               title="I-V Curve", x_axis_label="Voltage (V)", y_axis_label="Current (A)",
               tools="pan,wheel_zoom,box_zoom,reset,save")
    p.line('voltage', 'current', source=source, line_width=2, color="red")
    p.circle('voltage', 'current', source=source, size=4, color="red", alpha=0.6)
    # Enable responsive plot sizing within Bokeh figure itself
    p.sizing_mode = "stretch_both"
    return p

# --- ISPP Tuning Routine  ---
def ispp_tune_resistance_adaptive(
    row, col,
    target_resistance,
    tolerance=0.05,
    read_voltage=0.1,
    max_iterations=100,
    # --- SET Pulse Parameters ---
    set_pulse_initial_amplitude=0.35,
    set_pulse_max_amplitude=3.0,
    set_pulse_amplitude_step=0.1,
    set_pulse_width=1e-6,
    # --- RESET Pulse Parameters ---
    reset_pulse_initial_amplitude=-0.5,
    reset_pulse_max_amplitude=-3.0,
    reset_pulse_amplitude_step=-0.1,
    reset_pulse_width=1e-6,
    # --- Optional delay ---
    delay_between_steps=0.01
    ):
    """
    Tunes memristor resistance using ISPP with adaptive amplitude for BOTH SET and RESET.
    Returns history of the process.
    """
    print(f"\n--- Starting Adaptive ISPP for R{row}C{col} ---")
    print(f"Target: {target_resistance:.2f} Ohms (+/- {tolerance*100:.1f}%)")

    min_target = target_resistance * (1.0 - tolerance)
    max_target = target_resistance * (1.0 + tolerance)
    print(f"Target Range: [{min_target:.2f}, {max_target:.2f}] Ohms")

    current_set_amplitude = set_pulse_initial_amplitude
    current_reset_amplitude = reset_pulse_initial_amplitude
    final_resistance = None
    success = False

    history = {
        'iteration': [],
        'resistance': [],
        'set_amplitude_applied': [],
        'reset_amplitude_applied': []
    }

    for iteration in range(max_iterations):
        current_iter = iteration + 1
        print(f"\nIteration {current_iter}/{max_iterations}")
        print(f"Current Amplitudes: SET={current_set_amplitude:.3f}V, RESET={current_reset_amplitude:.3f}V")

        current_resistance = read_resistance(row, col, read_voltage)
        final_resistance = current_resistance

        history['iteration'].append(current_iter)
        history['resistance'].append(current_resistance)
        set_amp_applied_this_iter = np.nan
        reset_amp_applied_this_iter = np.nan

        if current_resistance is None:
            print("Error: Failed to read resistance. Aborting ISPP.")
            history['set_amplitude_applied'].append(set_amp_applied_this_iter)
            history['reset_amplitude_applied'].append(reset_amp_applied_this_iter)
            return False, None, history

        if min_target <= current_resistance <= max_target:
            print(f"Success: Target resistance reached ({current_resistance:.2f} Ohms)")
            success = True
            history['set_amplitude_applied'].append(set_amp_applied_this_iter)
            history['reset_amplitude_applied'].append(reset_amp_applied_this_iter)
            break

        pulse_applied = False
        if current_resistance > max_target:
            print(f"State: R > Target ({current_resistance:.2f} > {max_target:.2f}). Applying SET pulse.")
            amp_to_apply = min(current_set_amplitude, set_pulse_max_amplitude)
            set_amp_applied_this_iter = amp_to_apply
            if amp_to_apply != current_set_amplitude:
                 print(f"Info: Clamped SET amplitude to {set_pulse_max_amplitude:.3f} V")

            # --- Corrected SET Block Indentation ---
            if apply_voltage_pulse(row, col, amp_to_apply, set_pulse_width):
                 pulse_applied = True
                 # Increment SET amplitude for next time (if not already at max)
                 if current_set_amplitude < set_pulse_max_amplitude:
                      current_set_amplitude += set_pulse_amplitude_step
                      # Ensure it doesn't exceed max after stepping
                      current_set_amplitude = min(current_set_amplitude, set_pulse_max_amplitude)
                 # Reset RESET amplitude progression
                 current_reset_amplitude = reset_pulse_initial_amplitude
                 print(f"Next Amplitudes: SET={current_set_amplitude:.3f}V, RESET={current_reset_amplitude:.3f}V")
            else:
                 print("Error: Failed to apply SET pulse. Aborting.")
                 break
            # --- End Corrected Block ---

        elif current_resistance < min_target:
            print(f"State: R < Target ({current_resistance:.2f} < {min_target:.2f}). Applying RESET pulse.")
            amp_to_apply = max(current_reset_amplitude, reset_pulse_max_amplitude) # Max for negative limit
            reset_amp_applied_this_iter = amp_to_apply
            if amp_to_apply != current_reset_amplitude:
                 print(f"Info: Clamped RESET amplitude to {reset_pulse_max_amplitude:.3f} V")

            # --- Corrected RESET Block Indentation ---
            if apply_voltage_pulse(row, col, amp_to_apply, reset_pulse_width):
                pulse_applied = True
                # Increment RESET amplitude magnitude for next time (if not already at limit)
                if current_reset_amplitude > reset_pulse_max_amplitude: # Compare negative numbers correctly
                     current_reset_amplitude += reset_pulse_amplitude_step
                     # Ensure it doesn't exceed limit after stepping (use max for negative limit)
                     current_reset_amplitude = max(current_reset_amplitude, reset_pulse_max_amplitude)
                # Reset SET amplitude progression
                current_set_amplitude = set_pulse_initial_amplitude
                print(f"Next Amplitudes: SET={current_set_amplitude:.3f}V, RESET={current_reset_amplitude:.3f}V")
            else:
                print("Error: Failed to apply RESET pulse. Aborting.")
                break
            # --- End Corrected Block ---
        else:
            print("Warning: Logic error in SET/RESET decision. Aborting.")
            break

        history['set_amplitude_applied'].append(set_amp_applied_this_iter)
        history['reset_amplitude_applied'].append(reset_amp_applied_this_iter)

        if pulse_applied and delay_between_steps > 0:
            time.sleep(delay_between_steps)

    if not success and iteration >= max_iterations - 1 :
        print(f"Failure: Target not reached after {max_iterations} iterations.")

    while len(history['iteration']) > len(history['set_amplitude_applied']):
         history['set_amplitude_applied'].append(np.nan)
         history['reset_amplitude_applied'].append(np.nan)

    print(f"Final Resistance: {final_resistance:.2f} Ohms" if final_resistance is not None else "N/A")
    print(f"--- Adaptive ISPP Finished for R{row}C{col} ---")
    return success, final_resistance, history


# --- Plotting Function (Returns Figure) ---
def plot_ispp_history(history, target_resistance, tolerance, row, col):
    """Plots ISPP history and returns the Matplotlib Figure object."""
    if not history or not history['iteration']:
        print("No history data to plot.")
        fig, ax = plt.subplots(); ax.text(0.5, 0.5, 'No ISPP data generated.', ha='center', va='center'); plt.close(fig); return fig

    iterations = history['iteration']
    resistance = [r if np.isfinite(r) else np.nan for r in history['resistance']] # Handle potential Nones
    set_v = history['set_amplitude_applied']
    reset_v = history['reset_amplitude_applied']

    min_target = target_resistance * (1.0 - tolerance)
    max_target = target_resistance * (1.0 + tolerance)

    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = 'tab:green'; ax1.set_xlabel('Iteration'); ax1.set_ylabel('Resistance (Ohms)', color=color)
    ax1.plot(iterations, resistance, marker='o', ms=4, linestyle='-', color=color, label='Measured R')
    ax1.tick_params(axis='y', labelcolor=color); ax1.axhline(target_resistance, color='grey', linestyle='--', lw=1, label=f'Target R')
    ax1.axhline(min_target, color='grey', linestyle=':', lw=1, alpha=0.7); ax1.axhline(max_target, color='grey', linestyle=':', lw=1, alpha=0.7)
    ax1.fill_between(iterations, min_target, max_target, color='grey', alpha=0.15, label=f'Tolerance')
    if any(np.isfinite(r) for r in resistance): ax1.set_ylim(bottom=0, top=max(max_target*1.2, np.nanmax(resistance)*1.1))
    else: ax1.set_ylim(bottom=0)

    ax2 = ax1.twinx(); color_set = 'tab:red'; color_reset = 'tab:blue'
    ax2.set_ylabel('Applied Pulse Voltage (V)', color='black')
    ax2.plot(iterations, set_v, marker='^', linestyle='none', color=color_set, markersize=6, label='SET V')
    ax2.plot(iterations, reset_v, marker='v', linestyle='none', color=color_reset, markersize=6, label='RESET V')
    ax2.tick_params(axis='y', labelcolor='black'); ax2.axhline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

    ax1.legend(loc='upper left'); ax2.legend(loc='upper right')
    plt.title(f'ISPP History for R{row}C{col}', fontsize=12)
    plt.grid(True, which='both', linestyle=':', linewidth=0.5, alpha=0.7); fig.tight_layout()
    return fig


#################################################################
# --- Session Component Management ---
#################################################################
def get_or_create_session_components(session_id, header_info_widget):
    """Manages creation/caching of all components for a session."""
    print(f"Session Components: Checking cache for session {session_id}")
    components_key = f'selector_page_components_{session_id}'
      # --- CORRECTED CACHE CHECK ---
    if components_key in pn.state.cache:
        print("Session Components: Found components in cache.")
        # The line causing the KeyError was here and has been removed.
        # We simply return the cached dictionary directly. The callbacks
        # already have the correct reference from when they were created.
        return pn.state.cache[components_key]
    # --- END CORRECTION ---

    print("Session Components: Creating new components for session.")
    grid_cds = create_grid_cds(); selector_plot = create_selector_plot(grid_cds); selector_pane = pn.pane.Bokeh(selector_plot, min_height=260)
    iv_cds = create_iv_cds(); iv_plot = create_iv_plot(iv_cds); iv_pane = pn.pane.Bokeh(iv_plot, sizing_mode="stretch_both")
    selected_info = pn.widgets.StaticText(value="Selected: None", styles={'font-weight': 'bold', 'font-size': '9pt'}, align='center')
    initial_toggle_value = True; initial_button_type = 'success' if initial_toggle_value else 'warning'
    tap_enabled_toggle = pn.widgets.Toggle(name="Enable Select", value=initial_toggle_value, button_type=initial_button_type, margin=(0, 5), height=30, align='center')
    vmax_input = pn.widgets.FloatInput(name="Vmax (V)", value=1.5, step=0.1, width=90); vmin_input = pn.widgets.FloatInput(name="Vmin (V)", value=-1.5, step=0.1, width=90)
    step_input = pn.widgets.FloatInput(name="Step (V)", value=0.05, step=0.01, start=0.001, width=90); gate_input = pn.widgets.FloatInput(name="Gate V (V)", value=0.0, step=0.1, width=90)
    measure_button = pn.widgets.Button(name="Measure Selected Device", button_type="success", icon='settings-2', height=40)
    measure_all_button = pn.widgets.Button(name="Measure Full Array", button_type="primary", icon='grid', height=40, margin=(5,0,0,0))
    measurement_status = pn.widgets.StaticText(value="", styles={'font-size':'9pt', 'margin-left':'5px'})
    compliance_input = pn.widgets.FloatInput(
        name="I Compliance (A)", value=0.001, # Default 1mA
        step=1e-4, start=1e-9, # Allow small steps, positive values
        format='0.0e', # Scientific notation might be useful
        width=120, # Adjust width as needed
        # placeholder="e.g., 0.001 for 1mA" # Placeholder text not directly supported, use name
    )
    
    last_sel_key = f'selector_last_sel_{session_id}'; pn.state.cache[last_sel_key] = [None]
    callback_data = {'grid_cds': grid_cds, 'iv_cds': iv_cds, 'toggle': tap_enabled_toggle, 'info': selected_info, 'last_sel_tracker': pn.state.cache[last_sel_key], 'vmax': vmax_input, 'vmin': vmin_input, 'step': step_input, 'gate': gate_input, 'status': measurement_status, 'measure_all_button': measure_all_button,
                     'header_info': header_info_widget,'compliance': compliance_input}

    def handle_selection_change(attr, old, new):
        cb_grid_cds=callback_data['grid_cds']; cb_toggle=callback_data['toggle']; cb_info=callback_data['info']; cb_last_sel=callback_data['last_sel_tracker']; cb_status=callback_data['status']; cb_header_info=callback_data['header_info']
        if not cb_toggle.value: return
        print(f"Selection changed (Callback): {old} -> {new}"); current_selection_index=None; new_colors=list(cb_grid_cds.data['color'])
        if cb_last_sel[0] is not None and cb_last_sel[0]<len(new_colors): new_colors[cb_last_sel[0]]=DEFAULT_COLOR
        if new:
            current_selection_index=new[0]; selected_id=cb_grid_cds.data['id'][current_selection_index]
            info_text=f"Sel: {selected_id}"; header_text=f"Selected: {selected_id}"; cb_info.value=info_text; cb_header_info.value=header_text
            new_colors[current_selection_index]=SELECTED_COLOR; cb_last_sel[0]=current_selection_index; cb_status.value="Device selected. Click 'Measure'."
        else:
            cb_info.value="Sel: None"; cb_header_info.value="Selected: None"
            cb_last_sel[0]=None; cb_status.value="No device selected."
        cb_grid_cds.data['color']=new_colors

    def measure_single_device_callback(event):
        print(f"Measure button clicked: {event}"); 
        cb_iv_cds=callback_data['iv_cds']; cb_last_sel=callback_data['last_sel_tracker']; 
        cb_grid_cds=callback_data['grid_cds']; cb_status=callback_data['status']; vmin=callback_data['vmin'].value; vmax=callback_data['vmax'].value; step=callback_data['step'].value; gate_v=callback_data['gate'].value; selected_index=cb_last_sel[0]
        compliance = callback_data['compliance'].value 
        # Pass compliance to simulation/hardware if needed
        if selected_index is None: print("Measurement Error: No device selected."); cb_status.value="Error: No device selected!"; return
        selected_row=cb_grid_cds.data['row'][selected_index]; selected_col=cb_grid_cds.data['col'][selected_index]; selected_id=cb_grid_cds.data['id'][selected_index]; cb_status.value=f"Measuring {selected_id}..."; 
        iv_data=simulate_iv_curve(selected_row,selected_col,vmin,vmax,step,gate_v); 
        cb_iv_cds.data=iv_data; cb_status.value=f"Measured {selected_id}."; 
        print(f"Measurement complete for {selected_id}. Plot updated.")

    def update_toggle_color(event):
        toggle_widget=event.obj; is_on=event.new; toggle_widget.button_type='success' if is_on else 'warning'; toggle_widget.name="Active select ✔️" if is_on else "Inactive select ❌"; print(f"Toggle {'ON' if is_on else 'OFF'} - Color set to {toggle_widget.button_type}")

    async def measure_full_array_callback(event):
        print(f"Measure Full Array button clicked: {event}"); cb_grid_cds=callback_data['grid_cds']; cb_status=callback_data['status']; cb_measure_all_button=callback_data['measure_all_button']
        if pn.state.curdoc is None: print("Error: No document context."); cb_status.value="Error: Cannot run scan (no session context)."; return
        compliance = callback_data['compliance'].value # Read compliance value
        print(f"--- Using Compliance for full scan: {compliance:.3e} A ---") # Log compliance

        cb_measure_all_button.disabled=True; cb_measure_all_button.name="Measuring..."; cb_status.value="Starting full array scan..."; await asyncio.sleep(0.01); new_colors=[DEFAULT_COLOR]*(GRID_SIZE*GRID_SIZE); num_devices=GRID_SIZE*GRID_SIZE; measured_count=0; scan_error=None
        try:
            for idx in range(num_devices):
                row=cb_grid_cds.data['row'][idx]; col=cb_grid_cds.data['col'][idx]; 
                # Pass compliance to simulation/hardware if needed
                iv_data=simulate_iv_curve(row,col,FULL_SCAN_VMIN,FULL_SCAN_VMAX,FULL_SCAN_STEP,FULL_SCAN_GATE)
                try: current_at_v=np.interp(CONDUCTANCE_VOLTAGE,iv_data['voltage'],iv_data['current']); conductance=0 if abs(CONDUCTANCE_VOLTAGE)<1e-9 else current_at_v/CONDUCTANCE_VOLTAGE
                except Exception as e: print(f"Error calculating conductance for R{row}C{col}: {e}"); conductance=0
                norm_g=np.clip((conductance-MIN_CONDUCTANCE)/(MAX_CONDUCTANCE-MIN_CONDUCTANCE),0,1); color_index=int(norm_g*(len(COLOR_PALETTE)-1)); new_colors[idx]=COLOR_PALETTE[color_index]; measured_count+=1
                if measured_count%16==0: cb_status.value=f"Measuring... ({measured_count}/{num_devices})"; await asyncio.sleep(0)
            print("Full scan simulation complete. Scheduling grid color update.")
            def _apply_color_update(colors_to_apply):
                print("Applying color update via next_tick");
                try: current_data=dict(cb_grid_cds.data); current_data['color']=colors_to_apply; cb_grid_cds.data=current_data; print("Color update applied."); cb_status.value="Full array scan complete. Grid updated.";
                except Exception as e: print(f"Error applying color update in next_tick: {e}"); cb_status.value="Error updating grid visuals."
            pn.state.curdoc.add_next_tick_callback(lambda: _apply_color_update(new_colors)); cb_status.value="Scan complete. Updating grid..."
        except Exception as e: scan_error=e; cb_status.value=f"Error during scan: {e}"; print(f"Error during full array scan: {e}")
        finally: cb_measure_all_button.disabled=False; cb_measure_all_button.name="Measure Full Array"; print("Button re-enabled.")

    grid_cds.selected.on_change('indices',handle_selection_change); measure_button.on_click(measure_single_device_callback); tap_enabled_toggle.param.watch(update_toggle_color,'value'); measure_all_button.on_click(measure_full_array_callback)
    session_components={'selector_pane':selector_pane,'iv_pane':iv_pane,'toggle':tap_enabled_toggle,
                        'info':selected_info,'vmax_input':vmax_input,'vmin_input':vmin_input,'step_input':step_input,
                        'gate_input':gate_input, 'compliance_input': compliance_input, 
                        'measure_button':measure_button,'measurement_status':measurement_status,'measure_all_button':measure_all_button,'grid_cds':grid_cds}
    pn.state.cache[components_key]=session_components; return session_components

#################################################################
# --- Page Content Functions ---
#################################################################
def page_home(): return pn.Column(pn.pane.Markdown("## Home"), pn.pane.Markdown("Welcome!"))



# --- NEW Settings Page Function (Improved Layout) ---
def page_settings():
    """Creates the UI layout for the Keithley 2400 Settings page."""
    print("Rendering page_settings")
    global RESOURCE_MANAGER
    RESOURCE_MANAGER = None 
    
    # Initialize VISA Resource Manager if not already done
    if RESOURCE_MANAGER is None:
        try:
            RESOURCE_MANAGER = pyvisa.ResourceManager()
            print("VISA Resource Manager initialized.")
        except Exception as e:
            print(f"FATAL: Could not initialize VISA Resource Manager: {e}")
            # Display error clearly if VISA fails
            return pn.Column(
                 pn.pane.Markdown("## Keithley 2400 Settings"),
                 pn.pane.Alert(f"Error initializing VISA library: {e}. Please ensure VISA is installed and configured correctly.", alert_type="danger")
            )


    # --- Create Widgets for Settings ---
    # Use slightly wider inputs, can adjust later if needed
    widget_width = 140
    setting_source_func = pn.widgets.RadioButtonGroup(
        name="Source Function", options=['VOLT', 'CURR'], value='VOLT',
        button_type='primary', orientation='horizontal' # Horizontal looks better sometimes
    )
    setting_compliance_val = pn.widgets.FloatInput(
        name="I Compliance (A)", value=0.001, step=1e-4, start=1e-9,
        format='0.3e', width=widget_width
    )
    # Removed setting_compliance_label - name will be updated dynamically
    setting_nplc = pn.widgets.FloatInput(
        name="Integration (NPLC)", value=1, step=0.1, start=0.01, end=10,
        width=widget_width
    )
    setting_sense_mode = pn.widgets.RadioButtonGroup(
        name="Sense Mode", options=['2-Wire', '4-Wire'], value='2-Wire',
        button_type='default', orientation='horizontal'
    )
    setting_terminals = pn.widgets.RadioButtonGroup(
        name="Terminals", options=['Front', 'Rear'], value='Front',
         button_type='default', orientation='horizontal'
    )
    # Initial state OFF, matching danger type
    setting_output_state = pn.widgets.Toggle(
        name="Output OFF", value=False, button_type='danger', width=110, align='center'
    )

    # Buttons for actions
    read_button = pn.widgets.Button(name="Read Settings", icon='refresh', button_type='warning', width=180)
    apply_button = pn.widgets.Button(name="Apply Settings", icon='settings-2', button_type='success', width=180)
    status_text = pn.widgets.StaticText(value="Connect and Read Settings.", height=40, margin=(5,5)) # Initial message

    # --- Helper Function to Safely Interact with Instrument ---
    async def _instrument_action(action_type="query", command=None):
        # (Keep this helper function exactly the same as before)
        instrument = None; status_text.value = f"Connecting to {KEITHLEY_ADDRESS}..."; await asyncio.sleep(0.01)
        try:
            instrument = RESOURCE_MANAGER.open_resource(KEITHLEY_ADDRESS); instrument.timeout = 5000; instrument.write_termination = '\n'; instrument.read_termination = '\n'; instrument.write("*CLS")
            if action_type == "query":
                if command: response = instrument.query(command); instrument.close(); return response.strip()
                else: instrument.close(); return None
            elif action_type == "write":
                if command:
                    instrument.write(command); error = instrument.query(":SYST:ERR?"); instrument.close()
                    if 'No error' in error: return True, None
                    else: return False, error.strip()
                else: instrument.close(); return True, None
            else: instrument.close(); return None
        except pyvisa.errors.VisaIOError as e: status_text.value = f"VISA Error: {e}"; print(f"VISA Error communicating with {KEITHLEY_ADDRESS}: {e}"); instrument and instrument.close(); return None if action_type=="query" else (False, str(e))
        except Exception as e: status_text.value = f"General Error: {e}"; print(f"Unexpected Error: {e}\n{traceback.format_exc()}"); instrument and instrument.close(); return None if action_type=="query" else (False, str(e))


    # --- Callback to Read Settings (Modified to update compliance name) ---
    async def read_instrument_settings(event):
        print("Reading instrument settings...")
        read_button.loading = True; status_text.value = "Reading settings..."
        results = {}; commands = {'idn':'*IDN?', 'source_func':':SOUR:FUNC?', 'sense_mode':':SYST:RSEN?', 'compliance_curr':':SENS:CURR:PROT?', 'compliance_volt':':SENS:VOLT:PROT?', 'nplc_curr':':SENS:CURR:NPLC?', 'nplc_volt':':SENS:VOLT:NPLC?', 'output_state':':OUTP:STAT?', 'terminals':':ROUT:TERM?'}
        idn = await _instrument_action("query", commands['idn'])
        if idn is None: status_text.value += " (Failed to get IDN)"; read_button.loading=False; return
        status_text.value = f"Connected to: {idn}"; await asyncio.sleep(0.1)
        read_ok = True
        for key, cmd in commands.items():
            if key == 'idn': continue
            response = await _instrument_action("query", cmd)
            if response is None: status_text.value += f"\nError reading {key}!"; read_ok = False; break
            results[key] = response; await asyncio.sleep(0.05)
        if not read_ok: read_button.loading=False; return
        # Update widgets based on read results
        try:
            # --- Update Source Func FIRST ---
            read_source_func = results.get('source_func', 'VOLT')
            setting_source_func.value = read_source_func

            # --- Update Compliance Name and Value ---
            if read_source_func == 'VOLT':
                setting_compliance_val.name = "I Compliance (A)" # Update name
                setting_compliance_val.value = float(results.get('compliance_curr', 0.001))
                setting_nplc.value = float(results.get('nplc_volt', 1))
            else: # Sourcing Current
                setting_compliance_val.name = "V Compliance (V)" # Update name
                setting_compliance_val.value = float(results.get('compliance_volt', 20.0))
                setting_nplc.value = float(results.get('nplc_curr', 1))
            # --- End Compliance Update ---

            setting_sense_mode.value = '4-Wire' if int(results.get('sense_mode', 0)) == 1 else '2-Wire'
            is_on = (int(results.get('output_state', 0)) == 1)
            setting_output_state.value = is_on # Update toggle state FIRST
            setting_output_state.name = "Output ON" if is_on else "Output OFF" # Then update name
            setting_output_state.button_type = 'success' if is_on else 'danger' # Then update color
            term_val = results.get('terminals', 'FRON')
            setting_terminals.value = 'Front' if term_val == 'FRON' else 'Rear'
            status_text.value += "\nSettings read successfully."
        except Exception as e: status_text.value += f"\nError parsing settings: {e}"; print(f"Error updating widgets from instrument read: {e}")
        read_button.loading = False


    # --- Callback to Apply Settings ---
    async def apply_instrument_settings(event):
        # (Keep this callback exactly the same as before)
        print("Applying instrument settings..."); apply_button.loading = True; status_text.value = "Applying settings..."; await asyncio.sleep(0.01)
        commands_to_write = []
        commands_to_write.append(f":SOUR:FUNC {setting_source_func.value}")
        comp_val = setting_compliance_val.value
        if setting_source_func.value == 'VOLT': commands_to_write.append(f":SENS:CURR:PROT {comp_val:.4e}")
        else: commands_to_write.append(f":SENS:VOLT:PROT {comp_val:.4e}")
        nplc_val = max(0.01, min(10, setting_nplc.value))
        commands_to_write.append(f":SENS:CURR:NPLC {nplc_val}"); commands_to_write.append(f":SENS:VOLT:NPLC {nplc_val}")
        rsen_cmd = "ON" if setting_sense_mode.value == '4-Wire' else "OFF"; commands_to_write.append(f":SYST:RSEN {rsen_cmd}")
        term_cmd = "FRON" if setting_terminals.value == 'Front' else "REAR"; commands_to_write.append(f":ROUT:TERM {term_cmd}")
        out_cmd = "ON" if setting_output_state.value else "OFF"; commands_to_write.append(f":OUTP:STAT {out_cmd}")
        all_ok = True; final_msg = ""
        for cmd in commands_to_write:
            status_text.value = f"Sending: {cmd}"; success, error_msg = await _instrument_action("write", cmd)
            if not success: final_msg = f"Error applying '{cmd}': {error_msg}"; all_ok = False; break
            await asyncio.sleep(0.05)
        if all_ok: status_text.value = "Settings applied successfully."
        else: status_text.value = final_msg
        is_on = setting_output_state.value; setting_output_state.name = "Output ON" if is_on else "Output OFF"; setting_output_state.button_type = 'success' if is_on else 'danger'
        apply_button.loading = False


    # --- Callback for Output Toggle ---
    async def toggle_output_state(event):
        # (Keep this callback exactly the same as before)
        target_state = "ON" if event.new else "OFF"; print(f"Toggling output to {target_state}"); setting_output_state.name="Changing..."; setting_output_state.loading=True; await asyncio.sleep(0.01)
        success, error_msg = await _instrument_action("write", f":OUTP:STAT {target_state}"); setting_output_state.loading=False
        if success: setting_output_state.name = f"Output {target_state}"; setting_output_state.button_type = 'success' if event.new else 'danger'; status_text.value = f"Output turned {target_state}."
        else: status_text.value = f"Error setting output: {error_msg}"; setting_output_state.value = not event.new; setting_output_state.name = "Output ON" if setting_output_state.value else "Output OFF"; setting_output_state.button_type = 'success' if setting_output_state.value else 'danger'


    # --- Callback to update compliance name dynamically based on source func ---
    # This provides immediate feedback without needing to query the instrument
    def update_compliance_widget_name(event):
        if event.new == 'VOLT':
            setting_compliance_val.name = "I Compliance (A)"
        else:
            setting_compliance_val.name = "V Compliance (V)"

    # Attach callbacks
    read_button.on_click(read_instrument_settings)
    apply_button.on_click(apply_instrument_settings)
    setting_output_state.param.watch(toggle_output_state, 'value')
    setting_source_func.param.watch(update_compliance_widget_name, 'value') # Watch source function change

    # --- Arrange Layout (Improved Version) ---
    settings_layout = pn.Column(
        pn.pane.Markdown("## Keithley 2400 Settings"),
        pn.Card(
            # Use a single Row with two Columns for better alignment
            pn.Row(
                # --- Left Column ---
                pn.Column(
                    setting_source_func,
                    pn.layout.Spacer(height=15), # Add space
                    setting_compliance_val, # Name updated dynamically
                    pn.layout.Spacer(height=15),
                    setting_nplc,
                    # Adjust width if needed, or let them size naturally
                    # width=250
                ),
                pn.layout.Spacer(width=40), # Horizontal space between columns
                # --- Right Column ---
                pn.Column(
                    setting_sense_mode,
                    pn.layout.Spacer(height=15),
                    setting_terminals,
                    pn.layout.Spacer(height=35), # More space before toggle
                    setting_output_state,
                    # width=200
                ),
            ),
            title="Instrument Configuration", collapsible=False,
            styles={'border': '1px solid lightgrey'},
            width_policy='max', # Allow card to adapt width
            margin=(5, 10) # Add margin around card
        ),
        pn.Row(read_button, apply_button, margin=(15, 5)), # Buttons below card
        status_text,
        sizing_mode="stretch_width" # Allow outer column to adapt width
    )

    return settings_layout




def page_selector_main(session_components): 
    return pn.Column(pn.pane.Markdown("### I-V Curve Output"), 
                     session_components['iv_pane'], 
                     sizing_mode="stretch_both")



def page_ispp_tuning(session_components, header_info_widget):
    print("Rendering page_ispp_tuning")
    target_r_input = pn.widgets.FloatInput(name="Target R (Ohm)", value=20000, step=1000, start=100, width=150)
    tolerance_input = pn.widgets.FloatInput(name="Tolerance (+/-)", value=0.05, step=0.01, start=0.001, end=0.5, format='0.00%', width=120)
    run_ispp_button = pn.widgets.Button(name="Run ISPP Tune on Selected Device", button_type='primary', icon='player-play')
    ispp_status_text = pn.widgets.StaticText(value="Select device via sidebar grid first.", height=40, margin=(5,5))
    ispp_plot_pane = pn.pane.Matplotlib(None, sizing_mode="stretch_width", height=450)
    async def run_ispp_callback(event):
        print("Run ISPP button clicked")
        if pn.state.curdoc is None or pn.state.curdoc.session_context is None: ispp_status_text.value="Error: Session context lost."; return
        session_id = pn.state.curdoc.session_context.id; last_sel_key = f'selector_last_sel_{session_id}'
        current_session_components = get_or_create_session_components(session_id, header_info_widget)
        last_sel_tracker = pn.state.cache.get(last_sel_key);
        grid_cds = current_session_components.get('grid_cds')
        
        if not last_sel_tracker or last_sel_tracker[0] is None: ispp_status_text.value="Error: No device selected. Please select using sidebar grid."; ispp_plot_pane.object=None; return
        if not grid_cds: ispp_status_text.value = "Error: Grid data source not found in session."; ispp_plot_pane.object = None; return
        selected_index = last_sel_tracker[0]; row=grid_cds.data['row'][selected_index]; col=grid_cds.data['col'][selected_index]; device_id=grid_cds.data['id'][selected_index]
        target_r=target_r_input.value; tolerance=tolerance_input.value; run_ispp_button.disabled=True; run_ispp_button.name="Running ISPP..."; ispp_status_text.value=f"Running ISPP for {device_id}..."; ispp_plot_pane.object=None; await asyncio.sleep(0.01)
        try:
            success, final_r, history = ispp_tune_resistance_adaptive(row=row, col=col, target_resistance=target_r, tolerance=tolerance, max_iterations=100)
            if history: ispp_plot_pane.object = plot_ispp_history(history, target_r, tolerance, row, col)
            else: ispp_plot_pane.object = None
            if success: ispp_status_text.value = f"ISPP Complete for {device_id}: Success! Final R = {final_r:.2f} Ohms"
            else: ispp_status_text.value = f"ISPP Complete for {device_id}: Failed. Final R = {final_r:.2f} Ohms"
        except Exception as e: ispp_status_text.value=f"ISPP Error for {device_id}: {e}"; ispp_plot_pane.object=None; print(f"Error during ISPP call: {e}")
        finally: run_ispp_button.disabled=False; run_ispp_button.name="Run ISPP Tune on Selected Device"
    run_ispp_button.on_click(run_ispp_callback)
    ispp_page_layout = pn.Column(pn.pane.Markdown("## ISPP Resistance Tuning"), pn.Row(target_r_input, tolerance_input), run_ispp_button, ispp_status_text, pn.layout.Divider(), ispp_plot_pane, sizing_mode="stretch_width")
    return ispp_page_layout



#################################################################
# --- Routing Function for Main Content ---
#################################################################
def get_page_content(url_hash, header_info_widget):
    if pn.state.curdoc is None or pn.state.curdoc.session_context is None: return pn.pane.Markdown("Error: No session.")
    session_id = pn.state.curdoc.session_context.id; page_route = url_hash.lstrip('#'); print(f"Routing: Main content for hash '{page_route}'")
    session_components = get_or_create_session_components(session_id, header_info_widget)
    if page_route == "selector": return page_selector_main(session_components)
    elif page_route == "ispp_tuning": return page_ispp_tuning(session_components, header_info_widget)
    elif page_route == "settings": return page_settings()
    else: return page_home()



#################################################################
# --- Sidebar Content/Routing ---
#################################################################
def footer_home(): 
    return pn.widgets.StaticText(value="Status: Home", 
                                 styles={'font-size': '10pt', 'color': 'grey'})

def footer_settings(): 
    return pn.widgets.StaticText(value="Area: Config", 
                                 styles={'font-size': '10pt'})

# Measurement Controls (Conditional)
def get_sidebar_measurement_controls(url_hash, session_components):
    page_route = url_hash.lstrip('#')
    if page_route == 'selector':
        return pn.Column(pn.pane.Markdown("#### Measurement Setup"),
            pn.Row(session_components['vmin_input'], session_components['vmax_input']), 
            pn.Row(session_components['step_input'], session_components['gate_input']), 
            session_components['compliance_input'],
            session_components['measure_button'], 
            session_components['measure_all_button'], 
            session_components['measurement_status'], 
            sizing_mode='stretch_width')
    else: return None

# Selector Section (Persistent)
def get_sidebar_selector_section(session_components):
    if not all(k in session_components for k in ['toggle', 'info', 'selector_pane']): 
        print("Warning: Missing selector components for sidebar section."); 
        return pn.pane.Markdown("Error loading selector.")
    selector_layout = pn.Column(pn.pane.Markdown("#### Device Selection"), pn.Row(session_components['toggle'], session_components['info'], styles={'margin-bottom': '5px'}), session_components['selector_pane'], styles={'border': '1px solid lightgrey', 'padding': '5px', 'border-radius': '4px', 'background': '#fafafa'}, sizing_mode='stretch_width')
    return selector_layout

# Footer Content (Simplified)
def get_sidebar_footer_content(url_hash):
    page_route = url_hash.lstrip('#')
    if page_route == "settings": return footer_settings()
    else: return footer_home()

#################################################################
# --- Main Application Creation Function ---
#################################################################
def create_app():
    template = pnt.FastListTemplate(title="Crossbar Measurement Interface", sidebar_width=300, header_background="#4682B4")

    # --- Header Setup (Unchanged) ---
    header_selected_device_info = pn.widgets.StaticText(value="Selected: None", align='center', styles={'color': 'white', 'font-size': '10pt', 'margin': 'auto 5px'})
    template.header.append(pn.pane.Markdown("**Memristor Array Interface**", styles={'color': 'white', 'margin': 'auto 10px'}))
    template.header.append(header_selected_device_info)

    # --- Dynamic Navigation ---
    # 1. Define Navigation Items
    NAV_ITEMS = [
        {"name": "Home", "hash": "#home"},
        {"name": "Measurement", "hash": "#selector"},
        {"name": "ISPP Tuning", "hash": "#ispp_tuning"},
        {"name": "Settings", "hash": "#settings"},
    ]

    # 2. Function to generate navigation Markdown dynamically
    def create_dynamic_navigation(url_hash):
        # Determine the current active route, default to 'home' if hash is empty or None
        current_route = url_hash.lstrip('#') if url_hash else "home"
        # print(f"Updating navigation for route: {current_route}") # Optional: for debugging

        nav_links_md = "### Navigation\n<ul>\n"
        for item in NAV_ITEMS:
            item_route = item["hash"].lstrip('#')
            # Add the 'active' class if the item's route matches the current route
            css_class = ' class="active"' if item_route == current_route else ''
            nav_links_md += f'  <li><a href="{item["hash"]}"{css_class}>{item["name"]}</a></li>\n'
        nav_links_md += "</ul>"

        # Return a Markdown pane with the generated content and the stylesheet
        return pn.pane.Markdown(
            nav_links_md,
            sizing_mode="stretch_width",
            stylesheets=[custom_nav_css_scoped] # Apply stylesheet HERE
        )

    # 3. Bind the function to the URL hash and add to sidebar
    # REMOVE the old static navigation_md definition
    # navigation_md = pn.pane.Markdown(...) # DELETE THIS LINE

    # Bind the dynamic creation function to the hash parameter
    dynamic_navigation = pn.bind(create_dynamic_navigation, url_hash=pn.state.location.param.hash)

    # Add the bound, dynamic navigation pane to the sidebar
    template.sidebar.append(dynamic_navigation)
    template.sidebar.append(pn.layout.Divider()) # Keep the divider

    # --- Rest of the Sidebar/Main Content Setup (Unchanged) ---

    # Helper lambda to get session components, passing header widget
    get_current_session_components_with_header = lambda: get_or_create_session_components(pn.state.curdoc.session_context.id, header_selected_device_info)

    # Bind Dynamic Sidebar Sections
    dynamic_sidebar_controls = pn.bind(lambda url_hash: get_sidebar_measurement_controls(url_hash, get_current_session_components_with_header()), url_hash=pn.state.location.param.hash)
    template.sidebar.append(pn.Column(dynamic_sidebar_controls, sizing_mode='stretch_width', margin=(5, 5, 15, 5)))

    persistent_sidebar_selector = pn.bind(lambda _: get_sidebar_selector_section(get_current_session_components_with_header()), pn.state.location.param.hash) # Use hash change to trigger update if needed
    template.sidebar.append(pn.Column(persistent_sidebar_selector, sizing_mode='stretch_width', margin=(15, 5, 5, 5)))

    dynamic_sidebar_footer = pn.bind(get_sidebar_footer_content, url_hash=pn.state.location.param.hash)
    template.sidebar.append(pn.Column(dynamic_sidebar_footer, sizing_mode='stretch_width', margin=(15, 5, 5, 5)))

    # Bind Main Content Area (Pass header widget ref via lambda)
    dynamic_main_content = pn.bind(lambda url_hash: get_page_content(url_hash, header_selected_device_info), url_hash=pn.state.location.param.hash)
    template.main.append(pn.Column(dynamic_main_content, sizing_mode="stretch_both"))

    return template



# --- Serve the app ---
app_instance = create_app()
app_instance.servable()
