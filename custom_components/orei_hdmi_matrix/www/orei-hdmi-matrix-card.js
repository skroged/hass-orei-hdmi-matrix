class OreiHdmiMatrixCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="${this.config.name || 'HDMI Matrix Control'}">
          <div class="card-content">
            <div class="input-selector">
              <ha-selector-select 
                .hass=${hass} 
                .selector=${{select: {options: this.config.options}}}
                .value=${this.config.value}
                @value-changed=${this._valueChanged}>
              </ha-selector-select>
            </div>
            <div class="status-info">
              <div class="current-input">
                <span class="label">Current Input:</span>
                <span class="value">${this.config.value || 'None'}</span>
              </div>
              <div class="device-info">
                <span class="label">Device:</span>
                <span class="value">${this.config.device_name || 'HDMI Matrix'}</span>
              </div>
            </div>
          </div>
        </ha-card>
      `;
      this.content = this.querySelector(".card-content");
    }
    
    // Update the current value
    const valueElement = this.querySelector(".value");
    if (valueElement) {
      valueElement.textContent = this.config.value || 'None';
    }
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  _valueChanged(ev) {
    // Handle input selection change
    this.hass.callService("select", "select_option", {
      entity_id: this.config.entity,
      option: ev.detail.value
    });
  }

  static get styles() {
    return `
      <style>
        .card-content {
          padding: 16px;
        }
        .input-selector {
          margin-bottom: 16px;
        }
        .status-info {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .current-input, .device-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .label {
          font-weight: 500;
          color: var(--secondary-text-color);
        }
        .value {
          font-weight: 600;
          color: var(--primary-text-color);
        }
        ha-selector-select {
          width: 100%;
        }
      </style>
    `;
  }
}

customElements.define("orei-hdmi-matrix-card", OreiHdmiMatrixCard);

// Register for card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "orei-hdmi-matrix-card",
  name: "OREI HDMI Matrix",
  preview: false,
  description: "Custom card for OREI HDMI Matrix input selection",
});
