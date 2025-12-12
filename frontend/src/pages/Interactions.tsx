import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Form, Input, InputNumber, Button, Tabs } from 'antd';
import { useCommands } from '@/hooks/useCommands';

const { TabPane } = Tabs;

export const Interactions = () => {
  const [searchParams] = useSearchParams();
  const animeIdParam = searchParams.get('anime_id');
  const { loading, registerClick, registerView, registerRating } = useCommands();

  const [clickForm] = Form.useForm();
  const [viewForm] = Form.useForm();
  const [ratingForm] = Form.useForm();

  useEffect(() => {
    if (animeIdParam) {
      const animeId = parseInt(animeIdParam, 10);
      clickForm.setFieldsValue({ anime_id: animeId });
      viewForm.setFieldsValue({ anime_id: animeId });
      ratingForm.setFieldsValue({ anime_id: animeId });
    }
  }, [animeIdParam, clickForm, viewForm, ratingForm]);

  const handleClick = async (values: any) => {
    await registerClick(values);
    clickForm.resetFields();
  };

  const handleView = async (values: any) => {
    await registerView(values);
    viewForm.resetFields();
  };

  const handleRating = async (values: any) => {
    await registerRating(values);
    ratingForm.resetFields();
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Card title="Registrar Interacciones">
        <Tabs defaultActiveKey="click">
          <TabPane tab="Click" key="click">
            <Form
              form={clickForm}
              layout="vertical"
              onFinish={handleClick}
            >
              <Form.Item
                name="anime_id"
                label="Anime ID"
                rules={[{ required: true, message: 'Ingresa el Anime ID' }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item
                name="user_id"
                label="User ID"
                rules={[{ required: true, message: 'Ingresa el User ID' }]}
              >
                <Input placeholder="user123" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Registrar Click
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="Visualización" key="view">
            <Form
              form={viewForm}
              layout="vertical"
              onFinish={handleView}
            >
              <Form.Item
                name="anime_id"
                label="Anime ID"
                rules={[{ required: true, message: 'Ingresa el Anime ID' }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item
                name="user_id"
                label="User ID"
                rules={[{ required: true, message: 'Ingresa el User ID' }]}
              >
                <Input placeholder="user123" />
              </Form.Item>
              <Form.Item
                name="duration_seconds"
                label="Duración (segundos)"
                rules={[
                  { required: true, message: 'Ingresa la duración' },
                  { type: 'number', min: 0, message: 'La duración debe ser mayor o igual a 0' },
                ]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Registrar Visualización
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="Calificación" key="rating">
            <Form
              form={ratingForm}
              layout="vertical"
              onFinish={handleRating}
            >
              <Form.Item
                name="anime_id"
                label="Anime ID"
                rules={[{ required: true, message: 'Ingresa el Anime ID' }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item
                name="user_id"
                label="User ID"
                rules={[{ required: true, message: 'Ingresa el User ID' }]}
              >
                <Input placeholder="user123" />
              </Form.Item>
              <Form.Item
                name="rating"
                label="Calificación (0-10)"
                rules={[
                  { required: true, message: 'Ingresa la calificación' },
                  { type: 'number', min: 0, max: 10, message: 'La calificación debe estar entre 0 y 10' },
                ]}
              >
                <InputNumber min={0} max={10} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Registrar Calificación
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};
