import React, { useState } from 'react';
import { 
  FloatButton, 
  Modal, 
  Button, 
  Space,
  Tooltip 
} from 'antd';
import { 
  RobotOutlined, 
  MessageOutlined, 
  AudioOutlined,
  CloseOutlined 
} from '@ant-design/icons';
import Tasks from '../pages/Tasks';
import VoiceChat from './VoiceChat';

const FloatingChatBot = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState('chat'); // 'chat' or 'voice'

  const showChatModal = () => {
    setModalMode('chat');
    setIsModalVisible(true);
  };

  const showVoiceModal = () => {
    setModalMode('voice');
    setIsModalVisible(true);
  };

  const handleModalClose = () => {
    setIsModalVisible(false);
  };

  return (
    <>
      {/* 悬浮按钮组 */}
      <FloatButton.Group
        trigger="click"
        type="primary"
        style={{ right: 24, bottom: 24 }}
        icon={<RobotOutlined />}
        tooltip="AI助手"
      >
        <Tooltip title="文字聊天" placement="left">
          <FloatButton
            icon={<MessageOutlined />}
            onClick={showChatModal}
          />
        </Tooltip>
        <Tooltip title="语音交流" placement="left">
          <FloatButton
            icon={<AudioOutlined />}
            onClick={showVoiceModal}
          />
        </Tooltip>
      </FloatButton.Group>

      {/* 聊天模态框 */}
      <Modal
        title={
          <Space>
            <RobotOutlined style={{ color: '#1890ff' }} />
            {modalMode === 'chat' ? 'AI助手 - 文字聊天' : 'AI助手 - 语音交流'}
          </Space>
        }
        open={isModalVisible}
        onCancel={handleModalClose}
        footer={null}
        width={800}
        style={{ top: 20 }}
        bodyStyle={{ 
          padding: 0, 
          height: '75vh',
          overflow: 'hidden'
        }}
        destroyOnClose={true}
        closeIcon={<CloseOutlined />}
      >
        {modalMode === 'chat' && (
          <div style={{ height: '100%' }}>
            <Tasks />
          </div>
        )}
        
        {modalMode === 'voice' && (
          <VoiceChat />
        )}
      </Modal>
    </>
  );
};

export default FloatingChatBot;