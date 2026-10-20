# P3 prototype: vertex and fan-index uploads through a wgpu StagingBelt whose chunks come back when the frame's
# command buffer is submitted; with --uniforms, the uniforms too, written straight into a belt slice reserved for
# the frame's upper bound.
import sys
p = sys.argv[1] + '/src/renderer/wgpu.rs'
uniforms = '--uniforms' in sys.argv
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
sub('''    fan_index_buffer: wgpu::Buffer,
    stencil_buffer: Option<wgpu::Texture>,''', '''    fan_index_buffer: wgpu::Buffer,
    staging_belt: wgpu::util::StagingBelt,
    stencil_buffer: Option<wgpu::Texture>,''')
sub('''        Self {
            device,
            queue,
''', '''        Self {
            staging_belt: wgpu::util::StagingBelt::new(device.clone(), 1 << 20),
            device,
            queue,
''')
# move the encoder up and record the copies into it
sub('''        if !vertex_bytes.is_empty() {
            self.queue.write_buffer(&self.vertex_buffer, 0, vertex_bytes);
        }''', '''        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());
        if let Some(size) = wgpu::BufferSize::new(vertex_bytes.len() as u64) {
            self.staging_belt
                .write_buffer(&mut encoder, &self.vertex_buffer, 0, size)
                .copy_from_slice(vertex_bytes);
        }''')
sub('''        if !fan_index_bytes.is_empty() {
            self.queue.write_buffer(&self.fan_index_buffer, 0, fan_index_bytes);
        }''', '''        if let Some(size) = wgpu::BufferSize::new(fan_index_bytes.len() as u64) {
            self.staging_belt
                .write_buffer(&mut encoder, &self.fan_index_buffer, 0, size)
                .copy_from_slice(fan_index_bytes);
        }''')
sub('''        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());

        let mut render_pass_builder''', '''        let mut render_pass_builder''')
if uniforms:
    sub('''        let mut render_pass_builder''', '''        let uniform_view = self.staging_belt.write_buffer(
            &mut encoder,
            &self.uniform_buffer,
            0,
            wgpu::BufferSize::new(needed_slots * self.uniform_stride).unwrap(),
        );

        let mut render_pass_builder''')
    sub('''            self.uniform_buffer.clone(),
            self.uniform_stride,
            self.shader_module.clone(),''', '''            self.uniform_buffer.clone(),
            self.uniform_stride,
            uniform_view,
            self.shader_module.clone(),''')
    sub('''        // write_buffer is ordered ahead of the caller's submit.
        let uniform_staging = &pipeline_and_bindgroup_mapper.uniform_staging;
        debug_assert!(
            uniform_staging.len() as u64 <= self.uniform_buffer.size(),
            "a command recorded more than UNIFORM_SLOTS_PER_COMMAND uniform slots"
        );
        if !uniform_staging.is_empty() {
            self.queue.write_buffer(&self.uniform_buffer, 0, uniform_staging);
        }
''', '''        drop(pipeline_and_bindgroup_mapper);
''')
    sub('''    uniform_staging: Vec<u8>,
    current_uniforms: Option<UniformArray>,''', '''    uniform_view: wgpu::BufferViewMut,
    uniform_len: usize,
    current_uniforms: Option<UniformArray>,''')
    sub('''        uniform_buffer: wgpu::Buffer,
        uniform_stride: u64,
        shader_module: Rc<wgpu::ShaderModule>,''', '''        uniform_buffer: wgpu::Buffer,
        uniform_stride: u64,
        uniform_view: wgpu::BufferViewMut,
        shader_module: Rc<wgpu::ShaderModule>,''')
    sub('''            uniform_staging: Vec::new(),''', '''            uniform_view,
            uniform_len: 0,''')
    sub('''        if self.current_uniforms.as_ref() != Some(&uniforms) {
            let end = self.uniform_staging.len() + self.uniform_stride as usize;
            self.uniform_staging
                .extend_from_slice(bytemuck::cast_slice(uniforms.as_slice()));
            self.uniform_staging.resize(end, 0);
            self.current_uniforms = Some(uniforms);
        }
        // The current command's slot is the last one staged.
        let offset = (self.uniform_staging.len() - self.uniform_stride as usize) as u32;''', '''        if self.current_uniforms.as_ref() != Some(&uniforms) {
            let bytes: &[u8] = bytemuck::cast_slice(uniforms.as_slice());
            self.uniform_view.slice(self.uniform_len..self.uniform_len + bytes.len()).copy_from_slice(bytes);
            self.uniform_len += self.uniform_stride as usize;
            self.current_uniforms = Some(uniforms);
        }
        // The current command's slot is the last one staged.
        let offset = (self.uniform_len - self.uniform_stride as usize) as u32;''')
sub('''        let command_buffer = encoder.finish();
''', '''        self.staging_belt.finish_and_recall_on_submit(&encoder);
        let command_buffer = encoder.finish();
''')
open(p, 'w').write(s)
