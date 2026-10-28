# P1 prototype: viewport bind groups kept per target size; entries the last flush did not bind are dropped.
import sys
p = sys.argv[1] + '/src/renderer/wgpu.rs'
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
sub('''    viewport_bind_group_layout: wgpu::BindGroupLayout,
    /// Without and with a coverage mask.
    draw_layouts: [DrawLayout; 2],''', '''    viewport_bind_group_layout: wgpu::BindGroupLayout,
    viewport_bind_groups: HashMap<[u32; 2], (wgpu::BindGroup, u64)>,
    /// Without and with a coverage mask.
    draw_layouts: [DrawLayout; 2],''')
sub('''            viewport_bind_group_layout,
            draw_layouts,''', '''            viewport_bind_group_layout,
            viewport_bind_groups: HashMap::new(),
            draw_layouts,''')
sub('''            self.viewport_bind_group_layout.clone(),
            &mut self.stencil_buffer_for_textures,''', '''            self.viewport_bind_group_layout.clone(),
            &mut self.viewport_bind_groups,
            self.flush_count,
            &mut self.stencil_buffer_for_textures,''')
sub('''        let command_buffer = encoder.finish();

        evict_least_recently_used(''', '''        let command_buffer = encoder.finish();

        let flush = self.flush_count;
        self.viewport_bind_groups.retain(|_, (_, last_used)| *last_used == flush);

        evict_least_recently_used(''')
sub('''    viewport_bind_group_layout: wgpu::BindGroupLayout,
    rpass: Option<wgpu::RenderPass<'a>>,''', '''    viewport_bind_group_layout: wgpu::BindGroupLayout,
    viewport_bind_groups: &'a mut HashMap<[u32; 2], (wgpu::BindGroup, u64)>,
    flush_count: u64,
    rpass: Option<wgpu::RenderPass<'a>>,''')
sub('''        viewport_bind_group_layout: wgpu::BindGroupLayout,
        stencil_buffer_for_textures: &'a mut HashMap<wgpu::Texture, wgpu::Texture>,
        texture_view: wgpu::TextureView,''', '''        viewport_bind_group_layout: wgpu::BindGroupLayout,
        viewport_bind_groups: &'a mut HashMap<[u32; 2], (wgpu::BindGroup, u64)>,
        flush_count: u64,
        stencil_buffer_for_textures: &'a mut HashMap<wgpu::Texture, wgpu::Texture>,
        texture_view: wgpu::TextureView,''')
sub('''        let viewport_bind_group = Self::create_viewport_bind_group(&device, &screen_view, &viewport_bind_group_layout);
        Self {''', '''        let viewport_bind_group = Self::viewport_bind_group(
            &device,
            &viewport_bind_group_layout,
            viewport_bind_groups,
            flush_count,
            screen_view,
        );
        Self {''')
sub('''            viewport_bind_group_layout,
            rpass: None,''', '''            viewport_bind_group_layout,
            viewport_bind_groups,
            flush_count,
            rpass: None,''')
sub('''        self.viewport = viewport;
        self.viewport_bind_group =
            Self::create_viewport_bind_group(&self.device, &self.viewport, &self.viewport_bind_group_layout);
    }
''', '''        self.viewport = viewport;
        self.viewport_bind_group = Self::viewport_bind_group(
            &self.device,
            &self.viewport_bind_group_layout,
            self.viewport_bind_groups,
            self.flush_count,
            viewport,
        );
    }

    fn viewport_bind_group(
        device: &wgpu::Device,
        layout: &wgpu::BindGroupLayout,
        groups: &mut HashMap<[u32; 2], (wgpu::BindGroup, u64)>,
        flush_count: u64,
        viewport: [f32; 2],
    ) -> wgpu::BindGroup {
        let (group, last_used) = groups
            .entry([viewport[0] as u32, viewport[1] as u32])
            .or_insert_with(|| (Self::create_viewport_bind_group(device, &viewport, layout), flush_count));
        *last_used = flush_count;
        group.clone()
    }
''')
open(p, 'w').write(s)
