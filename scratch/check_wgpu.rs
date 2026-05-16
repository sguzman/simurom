fn main() {
    println!("Vulkan: {:?}", wgpu::Backends::VULKAN);
    println!("DX12: {:?}", wgpu::Backends::DX12);
    println!("Metal: {:?}", wgpu::Backends::METAL);
    println!("GL: {:?}", wgpu::Backends::GL);
    println!("All: {:?}", wgpu::Backends::all());
}
