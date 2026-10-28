# P2 prototype: the uniform staging Vec keeps its capacity across flushes.
import sys
p = sys.argv[1] + '/src/renderer/wgpu.rs'
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
sub('''    uniform_stride: u64,
    vertex_buffer: wgpu::Buffer,
    fan_indices: FanIndices,''', '''    uniform_stride: u64,
    uniform_staging: Vec<u8>,
    vertex_buffer: wgpu::Buffer,
    fan_indices: FanIndices,''')
sub('''            uniform_stride,
            vertex_buffer,
            fan_indices: FanIndices::default(),''', '''            uniform_stride,
            uniform_staging: Vec::new(),
            vertex_buffer,
            fan_indices: FanIndices::default(),''')
sub('''            self.uniform_buffer.clone(),
            self.uniform_stride,
            self.shader_module.clone(),''', '''            self.uniform_buffer.clone(),
            self.uniform_stride,
            std::mem::take(&mut self.uniform_staging),
            self.shader_module.clone(),''')
sub('''        if !uniform_staging.is_empty() {
            self.queue.write_buffer(&self.uniform_buffer, 0, uniform_staging);
        }
''', '''        if !uniform_staging.is_empty() {
            self.queue.write_buffer(&self.uniform_buffer, 0, uniform_staging);
        }
        self.uniform_staging = std::mem::take(&mut pipeline_and_bindgroup_mapper.uniform_staging);
''')
sub('''        uniform_buffer: wgpu::Buffer,
        uniform_stride: u64,
        shader_module: Rc<wgpu::ShaderModule>,''', '''        uniform_buffer: wgpu::Buffer,
        uniform_stride: u64,
        mut uniform_staging: Vec<u8>,
        shader_module: Rc<wgpu::ShaderModule>,''')
sub('''        Self {
            device: device.clone(),
            empty_texture_view,
            sampler_cache,
            uniform_buffer,
            uniform_stride,
            uniform_staging: Vec::new(),''', '''        uniform_staging.clear();
        Self {
            device: device.clone(),
            empty_texture_view,
            sampler_cache,
            uniform_buffer,
            uniform_stride,
            uniform_staging,''')
open(p, 'w').write(s)
