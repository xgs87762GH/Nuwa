import React from 'react';
import {
  Modal,
  Spin,
  Alert,
  Tag,
  Badge,
  Divider,
  Button
} from 'antd';
import {
  ToolOutlined,
  LinkOutlined,
  UserOutlined
} from '@ant-design/icons';

const ToolDetailModal = ({
  open,
  onClose,
  selectedTool,
  loading,
  t,
  getStatusInfo,
  formatTime
}) => {
  return (
    <Modal
      className="tools-detail-modal"
      title={null}
      open={open}
      onCancel={onClose}
      footer={null}
      width={900}
      bodyStyle={{ padding: 0 }}
      closeIcon={null}
      maskClosable={true}
    >
      <div className="modal-wrapper">
        <div className="modal-header">
          <div className="modal-header-content">
            <div className="modal-title-section">
              <ToolOutlined className="modal-title-icon" />
              <div className="modal-title-text">
                <h2 className="modal-title">{selectedTool?.name || t('tools.toolDetails')}</h2>
                {selectedTool?.version && (
                  <span className="modal-version">v{selectedTool.version}</span>
                )}
              </div>
            </div>
            <button className="modal-close-btn" onClick={onClose} title="关闭">✕</button>
          </div>
        </div>

        <div className="modal-content">
          <Spin spinning={loading}>
            {selectedTool?.error ? (
              <Alert
                message={t('tools.error')}
                description={selectedTool.error}
                type="error"
                showIcon
                className="modal-alert"
              />
            ) : selectedTool ? (
              <div className="modal-body-content">
                <section className="modal-section">
                  <h3 className="section-title">{t('tools.basicInfo')}</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="info-label">{t('tools.toolName')}</span>
                      <span className="info-value">{selectedTool.name}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">{t('tools.version')}</span>
                      <span className="info-value">{selectedTool.version}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">{t('tools.status')}</span>
                      <span className="info-value">
                        {(() => {
                          const statusInfo = getStatusInfo(selectedTool.status);
                          return (
                            <Badge status={statusInfo.color} text={statusInfo.text} />
                          );
                        })()}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">{t('tools.enabled')}</span>
                      <span className="info-value">
                        {selectedTool.is_enabled ? (
                          <Tag color="success">{t('tools.statusTypes.enabled')}</Tag>
                        ) : (
                          <Tag>{t('tools.statusTypes.notEnabled')}</Tag>
                        )}
                      </span>
                    </div>
                    <div className="info-item full-width">
                      <span className="info-label">{t('tools.registeredAt')}</span>
                      <span className="info-value">{formatTime(selectedTool.registered_at)}</span>
                    </div>
                    {selectedTool.description && (
                      <div className="info-item full-width">
                        <span className="info-label">{t('tools.description')}</span>
                        <span className="info-value">{selectedTool.description}</span>
                      </div>
                    )}
                  </div>
                </section>

                {selectedTool.tags && selectedTool.tags.length > 0 && (
                  <section className="modal-section">
                    <h3 className="section-title">{t('tools.tags')}</h3>
                    <div className="tags-container">
                      {selectedTool.tags.map(tag => (
                        <Tag key={tag} className="modal-tag">{tag}</Tag>
                      ))}
                    </div>
                  </section>
                )}

                {selectedTool.metadata && (
                  <section className="modal-section">
                    <h3 className="section-title">{t('tools.detailInfo')}</h3>
                    <div className="metadata-container">
                      {selectedTool.metadata.author && (
                        <div className="metadata-item">
                          <span className="metadata-label"><UserOutlined /> {t('tools.author')}</span>
                          <span className="metadata-value">{selectedTool.metadata.author}</span>
                        </div>
                      )}
                      {selectedTool.metadata.license && (
                        <div className="metadata-item">
                          <span className="metadata-label">{t('tools.license')}</span>
                          <span className="metadata-value">{selectedTool.metadata.license}</span>
                        </div>
                      )}
                      {selectedTool.metadata.keywords && selectedTool.metadata.keywords.length > 0 && (
                        <div className="metadata-item">
                          <span className="metadata-label">{t('tools.keywords')}</span>
                          <div className="metadata-tags">
                            {selectedTool.metadata.keywords.map(keyword => (
                              <Tag key={keyword} className="modal-tag">{keyword}</Tag>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedTool.metadata.requirements && selectedTool.metadata.requirements.length > 0 && (
                        <div className="metadata-item">
                          <span className="metadata-label">{t('tools.dependencies')}</span>
                          <div className="metadata-tags">
                            {selectedTool.metadata.requirements.map((req, index) => (
                              <Tag key={index} className="modal-tag modal-tag-req">{req}</Tag>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedTool.metadata.urls && Object.keys(selectedTool.metadata.urls).length > 0 && (
                        <div className="metadata-item">
                          <span className="metadata-label">{t('tools.relatedLinks')}</span>
                          <div className="metadata-links">
                            {Object.entries(selectedTool.metadata.urls).map(([key, url]) => (
                              <a key={key} href={url} target="_blank" rel="noopener noreferrer" className="modal-link">
                                <LinkOutlined />
                                <span>{key}</span>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </section>
                )}

                <section className="modal-section modal-debug">
                  <details className="debug-details">
                    <summary className="debug-summary">{t('tools.viewRawData')}</summary>
                    <pre className="debug-pre">{JSON.stringify(selectedTool, null, 2)}</pre>
                  </details>
                </section>
              </div>
            ) : null}
          </Spin>
        </div>

        <div className="modal-footer">
          <Button onClick={onClose} className="modal-footer-btn">{t('tools.close')}</Button>
        </div>
      </div>
    </Modal>
  );
};

export default ToolDetailModal;
