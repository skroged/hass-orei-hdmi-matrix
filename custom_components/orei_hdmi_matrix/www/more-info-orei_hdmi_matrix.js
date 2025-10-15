import { html, css, LitElement } from "https://unpkg.com/lit@3.1.0/index.js?module";

class MoreInfoOreiHdmiMatrix extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      stateObj: { type: Object },
    };
  }

  static get styles() {
    return css`
        .container {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 16px;
        }
        .input-selector {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .label {
          font-weight: 500;
          color: var(--secondary-text-color);
        }
        .selector {
          width: 100%;
        }
        .device-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-top: 1px solid var(--divider-color);
        }
        .info-label {
          font-weight: 500;
          color: var(--secondary-text-color);
        }
        .info-value {
          font-weight: 600;
          color: var(--primary-text-color);
        }
      `;
  }

  render() {
    if (!this.stateObj) {
      return html`<div class="container">Entity not found</div>`;
    }

    const options = this.stateObj.attributes.options || [];
    const currentValue = this.stateObj.state;
    const deviceName = this.stateObj.attributes.friendly_name || "HDMI Matrix";

    return html`
      <div class="container">
        <div class="input-selector">
          <div class="label">Select Input:</div>
          <ha-select
            class="selector"
            .value=${currentValue}
            @change=${this._handleSelectionChange}
          >
            ${options.map(
              (option) => html`
                <mwc-list-item .value=${option}>${option}</mwc-list-item>
              `
            )}
          </ha-select>
        </div>
        
        <div class="device-info">
          <span class="info-label">Device:</span>
          <span class="info-value">${deviceName}</span>
        </div>
        
        <div class="device-info">
          <span class="info-label">Current Input:</span>
          <span class="info-value">${currentValue || "None"}</span>
        </div>
      </div>
    `;
  }

  _handleSelectionChange(ev) {
    const newValue = ev.target.value;
    if (newValue !== this.stateObj.state) {
      this.hass.callService("select", "select_option", {
        entity_id: this.stateObj.entity_id,
        option: newValue,
      });
    }
  }
}

customElements.define("more-info-orei_hdmi_matrix", MoreInfoOreiHdmiMatrix);
